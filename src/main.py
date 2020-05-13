import typing
import codecs

from src.configuration import ConfigReader, config_reader
from src.container import TripletContainer
from src.external.phrase_normalizer import RestletPhraseNormalizer, PhaseNormalizerCategory
from src.mapping_defaults.named_entity import NamedEntitiesMapping
from src.mapping_defaults.propbank import PropBankMapping
from src.pipes.coreference import CoReferencePipe
from src.pipes.named_entity import NamedEntitiesPipe
from src.pipes.propbank import PropBankPipe
from src.readers.coreference import CoReferenceContentAnnotationReader
from src.readers.named_entity import NamedEntitiesContentAnnotationReader
from src.readers.propbank import PropBankContentAnnotationReader, PropBankMergedFormatAnnotationReader

named_entities_debug = False
co_reference_debug = False

#data_file = open(config_reader.get_propbank_resource_file_path(), "r", encoding="utf-8")
#content = ""
#try:
#    content = data_file.read()
#finally:
#    data_file.close()
#annotation_reader=PropBankMergedFormatAnnotationReader(content)


# Define the pipeline
pipe_line = [
    PropBankPipe(PropBankMapping(), debug_mode=True),
    NamedEntitiesPipe(NamedEntitiesMapping(), phrase_normalizer=RestletPhraseNormalizer(), debug_mode=named_entities_debug),
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
