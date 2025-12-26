from dotenv import load_dotenv
import os
load_dotenv()
api = os.getenv('ANTHROPIC_API_KEY')
if not api:
    print('No ANTHROPIC_API_KEY found in environment or .env')
    raise SystemExit(1)

import importlib
anth = importlib.import_module('anthropic')
print('anthropic module:', anth)
client = None
if hasattr(anth, 'Anthropic'):
    client = anth.Anthropic(api_key=api)
elif hasattr(anth, 'Client'):
    client = anth.Client(api_key=api)
else:
    client = anth

print('Client type:', type(client))
attrs = sorted([a for a in dir(client) if not a.startswith('_')])
print('Top-level attributes on client:')
for a in attrs:
    print(' -', a)

# check nested attributes like chat, responses, completions
for name in ('completions','responses','chat','messages'):
    print(name, 'present:', hasattr(client, name))

# Attempt to introspect responses/completions objects if present
for name in ('completions','responses','chat','messages'):
    if hasattr(client, name):
        obj = getattr(client, name)
        print(f'--- {name} methods ---')
        print([m for m in dir(obj) if not m.startswith('_')][:20])
