import typing
import codecs
import i18n

from Code.configuration import ConfigReader
from Code.container import TripletContainer
from Code.mapping_defaults.named_entities import NamedEntitiesMapping
from Code.mapping_defaults.propbank import PropBankMapping
from Code.pipes.coreference import CoReferencePipe
from Code.pipes.named_entity import NamedEntitiesPipe
from Code.pipes.propbank import PropBankPipe

named_entities_debug = True
co_reference_debug = True

i18n.load_path.append('../translation')
i18n.set('locale', 'lv')
i18n.set('fallback', 'lv')

# Define the pipeline
pipe_line = [
    PropBankPipe(PropBankMapping(), None),
    NamedEntitiesPipe(NamedEntitiesMapping(), debug_mode=named_entities_debug),
    CoReferencePipe(debug_mode=co_reference_debug)
]

# The magic
triplet_list: typing.List[TripletContainer] = []
for p in pipe_line:
    triplet_list = p.process(triplet_list)

for p in pipe_line:
    print(f"Calculation ran {p.last_run_time:0.4f} seconds for {p}")

# Store in file
f = codecs.open(ConfigReader().get_output_file_path(), "w", "utf-8")
total = len(triplet_list)
with_co_reference = 0
with_named_entities = 0

for triplet in triplet_list:
    triplet.print(f)
    if triplet.has_co_reference_entry:
        with_co_reference += 1
    if triplet.has_named_entities_entry:
        with_named_entities += 1

if named_entities_debug or co_reference_debug:
    f.write("\r\n======= Statistics:\r\n")
    f.write(f"Total PropBank entries: {total}\r\n")
if named_entities_debug:
    f.write(f"Entries matched with named entities: {with_named_entities}\r\n")
if co_reference_debug:
    f.write(f"Entries matched with co references: {with_co_reference}\r\n")
f.close()
