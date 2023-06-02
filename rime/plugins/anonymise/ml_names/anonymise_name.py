from transformers import pipeline

# There's nothing special about this particular model or revision. They are just what pipeline('ner') gave me by
# default.
AI_NER_MODEL = 'dbmdz/bert-large-cased-finetuned-conll03-english'
AI_NER_REVISION = 'f2482bf'

_tokeniser = pipeline('ner', model=AI_NER_MODEL, revision=AI_NER_REVISION, aggregation_strategy='first')


def do_name_anonymisation(value):
    """
    Use a named entity recognition model to replace names with 'Anon'.
    """
    tokens = _tokeniser(value)
    new_value = []
    last_end = 0

    for token in sorted(tokens, key=lambda t: t['start']):
        if token['entity_group'] == 'PER':
            new_value.append(value[last_end:token['start']])
            new_value.append('Anon')
            last_end = token['end']

    new_value.append(value[last_end:])
    return ''.join(new_value)
