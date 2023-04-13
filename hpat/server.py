import contextlib
import copy
import http.server
import json
import socketserver
import time

import layer_noun_phrase
from hpat import (
    DataSequence,
)
from main_constituent import layer_words, layer_parts_of_speech, layer_phrases, layer_sentence, \
    layer_next, hierarchy


@contextlib.contextmanager
def timer(name):
    t1 = time.perf_counter()
    yield
    t2 = time.perf_counter()
    print(f"{name}: {(t2 - t1) * 1000:.02f}usec")


def find_main_noun(full_seq, match):
    dependant = full_seq.find_dependant_matches(match.id)
    dependant = [full_seq.match_by_id[x] for x in dependant
                 if full_seq.match_by_id[x].concept == 'MainNounPart']
    try:
        assert len(dependant) == 1
    except AssertionError:
        return match
    main_slot = dependant[0].slot

    for sub_match_id in match.depends_on_matches:
        if full_seq.match_by_id[sub_match_id].slot == main_slot:
            return find_main_noun(full_seq, full_seq.match_by_id[sub_match_id])
    raise ValueError()


def process_sentence(full_seq, sentence_match):
    seq = copy.deepcopy(full_seq)
    seq.clean_matches(sentence_match.id)

    for match_id in sentence_match.depends_on_matches:
        match = seq.match_by_id[match_id]
        if match.concept.endswith('NounPhrase'):
            main_match = find_main_noun(full_seq, match)
            breakpoint()
            pass

    return seq


def process(text):
    seq = DataSequence.from_string(text)

    with timer('words'):
        layer_words(seq)
    with timer('pos'):
        layer_parts_of_speech(seq)
    with timer('noun_phrases'):
        layer_noun_phrase.apply(seq)
    # with timer('phrases'):
    #     layer_phrases(seq)
    with timer('sentence'):
        layer_sentence(seq)
    with timer('next'):
        layer_next(seq)

    for match in seq.elements[1].matches:
        if match.concept != 'Sentence':
            continue
        if match.size != seq.size - 2:
            continue
        seq = process_sentence(seq, match)
        break
        breakpoint()
        pass

    # clause_match = sorted(seq.elements[1].matches, key=lambda x: x.size)[-1]
    # if clause_match.concept.endswith('Sentence'):
    #     seq.clean_matches(clause_match)

    # seq.keep_only(['NounPhrase', ], hierarchy=hierarchy)

    data = []
    ids = set()

    for elem in seq.elements:
        for match in elem.matches:
            if match.id in ids:
                continue
            # if match.concept not in {'Space', 'Word', 'WordSeparator', 'Verb', 'Noun', 'Determinant'}:
            #     continue
            # if match.concept in {'Character', 'Letter', 'WordSeparator', 'Word'}:
            #     continue
            # if match.concept in {'SingularNoun', 'Determinant', 'NumberlessVerb', 'ImperativeVerb', 'PrepositionOfPlace', 'PrepositionOfLocation', 'SingularVerb', 'HelpingVerb'}:
            #     continue

            ids.add(match.id)
            data.append({
                "id": match.id,
                "concept": match.concept,
                "start": match.start_idx,
                "size": match.size,
                "depends": match.depends_on_matches,
            })

    id_to_idx = {}
    for idx, match in enumerate(data):
        id_to_idx[match['id']] = idx
        match['id'] = idx

    deps = {}
    for match in data:
        match['depends'] = [id_to_idx[x] for x in match['depends'] if x in id_to_idx]
        deps[match['id']] = match['depends']

    def get_deps(idx):
        result = []
        for dep in deps.get(idx, []):
            result.append(dep)
            result.extend(get_deps(dep))

        return result

    for match in data:
        match['depends'] = sorted(list(set(get_deps(match['id']))))

    return data


class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    def reply(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.end_headers()
        data = json.dumps(data)
        self.wfile.write(data.encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode()
        try:
            data = json.loads(post_body)
        except json.JSONDecodeError:
            return self.reply(400, {"error": "Can't parse json"})

        if 'text' not in data:
            return self.reply(400, {"error": "No text provided"})

        result = process(data['text'])

        self.reply(200, {
            "result": result
        })


socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer(('0.0.0.0', 8080), MyRequestHandler)

server.serve_forever()
