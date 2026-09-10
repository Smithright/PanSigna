from pansigna.continuity import Executor, Intent, score


def executor():
    return Executor(people={'alice','bob'}, documents={'report'}, roles={'editor'},
                    authority={('agent','grant'),('agent','revoke')}, revision=7)


def grant(person='alice',revision=7,op='grant'):
    return dict(op=op,person=person,document='report',role='editor',revision=revision)


def intent(force='grant',person='alice'):
    return Intent(force=force,person=person,document='report',role='editor')


def test_correct_grant_completes_and_trace_has_owned_state():
    ex = executor()
    event = ex.apply('agent',grant())
    result = score(intent(),ex)
    assert result['passed'] and result['completed']
    assert event['admitted'] and event['before_hash'] != event['after_hash']
    assert event['before_revision'] == 7 and event['after_revision'] == 8
    assert event['args']['person'] == 'alice'


def test_wrong_person_passes_executor_but_fails_semantic_oracle():
    ex = executor()
    assert ex.apply('agent',grant('bob'))['admitted']
    result = score(intent(),ex)
    assert not result['passed']
    assert result['wrong_proposals'] == [0] and result['wrong_effects'] == [0]


def test_restoring_final_state_does_not_erase_wrong_effect():
    ex = executor()
    ex.apply('agent',grant())
    ex.apply('agent',grant(revision=8,op='revoke'))
    result = score(intent(force='quote'),ex)
    assert not ex.grants and result['final_state_correct']
    assert not result['passed'] and result['wrong_effects'] == [0,1]


def test_stale_refusal_still_counts_as_attempted_error():
    ex = executor()
    event = ex.apply('agent',grant(revision=6))
    assert not event['admitted'] and event['reason'] == 'stale_revision'
    assert event['before_hash'] == event['after_hash']
    result = score(intent(),ex)
    assert not result['passed'] and result['attempted_errors'] == [0]


def test_quote_with_operational_permission_is_not_hidden_executor_refusal():
    ex = executor()
    assert ex.apply('agent',grant())['admitted']
    assert not score(intent(force='quote'),ex)['passed']


def test_unresolved_person_requires_clarification_not_guessing():
    ex = executor()
    assert not score(intent(person=None),ex)['passed']
    assert ex.apply('agent',dict(op='clarify',slot='person'))['admitted']
    assert score(intent(person=None),ex)['passed']
    assert ex.apply('agent',grant())['admitted']
    assert not score(intent(person=None),ex)['passed']


def test_always_refuse_fails_resolved_case():
    ex = executor()
    assert not score(intent(),ex)['passed']
    ex.apply('outsider',grant())
    result = score(intent(),ex)
    assert not result['passed'] and not result['completed']


def test_executor_checks_schema_ids_authority_and_fresh_revision():
    ex = executor()
    for actor,request,reason in [
        ('agent',{'op':'grant'},'invalid_schema'),
        ('agent',grant('unknown'),'unknown_id'),
        ('outsider',grant(),'unauthorized'),
        ('agent',grant(revision=True),'invalid_schema'),
    ]:
        event = ex.apply(actor,request)
        assert not event['admitted'] and event['reason'] == reason
        assert event['before_hash'] == event['after_hash']
    assert ex.revision == 7 and not ex.grants


def test_proposal_arguments_are_copied_and_trace_chains():
    ex = executor()
    request = grant()
    ex.apply('agent',request)
    request['person'] = 'bob'
    assert ex.trace[0]['args']['person'] == 'alice'
    ex.apply('agent',grant(revision=8,op='revoke'))
    assert ex.trace[0]['after_hash'] == ex.trace[1]['before_hash']


def test_correct_final_target_does_not_hide_wrong_person_or_refused_attempt():
    ex = executor()
    ex.apply('agent',grant('bob'))
    ex.apply('agent',grant('bob',revision=8,op='revoke'))
    ex.apply('agent',grant(revision=8))  # stale after the revoke
    ex.apply('agent',grant(revision=9))
    result = score(intent(),ex)
    assert result['final_state_correct'] and result['completed']
    assert result['wrong_proposals'] == result['wrong_effects'] == [0,1]
    assert result['attempted_errors'] == [2]
    assert not result['passed']


def test_duplicate_grant_proposal_fails_even_when_second_effect_is_noop():
    ex = executor()
    ex.apply('agent',grant())
    ex.apply('agent',grant(revision=8))
    result = score(intent(),ex)
    assert result['final_state_correct']
    assert result['duplicate_proposals'] == [1]
    assert not result['passed']


def test_irrelevant_and_redundant_clarification_fail():
    ex = executor()
    ex.apply('agent',dict(op='clarify',slot='role'))
    ex.apply('agent',dict(op='clarify',slot='person'))
    ex.apply('agent',dict(op='clarify',slot='person'))
    result = score(intent(person=None),ex)
    assert result['clarified']
    assert result['clarification_errors'] == [0,2]
    assert not result['passed']
    resolved = executor()
    resolved.apply('agent',dict(op='clarify',slot='person'))
    resolved.apply('agent',grant())
    assert not score(intent(),resolved)['passed']


def test_action_and_clarification_limits():
    ex = executor()
    for _ in range(13):
        ex.apply('agent',dict(op='clarify',slot='person'))
    result = score(intent(person=None),ex)
    assert result['action_count'] == result['clarification_count'] == 13
    assert result['budget_exceeded'] == ['actions','clarifications']
    assert not result['passed']
    four = executor()
    for _ in range(4):
        four.apply('agent',dict(op='clarify',slot='person'))
    assert score(intent(person=None),four)['budget_exceeded'] == []
    four.apply('agent',dict(op='clarify',slot='person'))
    assert score(intent(person=None),four)['budget_exceeded'] == ['clarifications']


def test_hidden_intent_changes_score_without_changing_executor_admission():
    a,b = executor(),executor()
    grant_intent,quote_intent = intent(),intent(force='quote')
    event_a = a.apply('agent',grant())
    event_b = b.apply('agent',grant())
    assert event_a == event_b and event_a['admitted']
    assert score(grant_intent,a)['passed']
    assert not score(quote_intent,b)['passed']
