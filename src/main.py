import logging
import typing
import codecs

from src.configuration import ConfigReader, config_reader

# use to log (can be displayed to user!):
# log_stream = StringIO() | stream=log_stream, datefmt='%H:%M:%S', | print(log_stream.getvalue())
logging.basicConfig(level=config_reader.get_logger_severity_level(), format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')

from src.container.base import IContainer
from src.external.phrase_normalizer import RestletPhraseNormalizer, PhaseNormalizerCategory
from src.mapping_defaults.named_entity import NamedEntitiesMapping
from src.mapping_defaults.propbank import PropBankMapping
from src.pipes.coreference import CoReferencePipe
from src.pipes.named_entity import NamedEntitiesPipe
from src.pipes.propbank import PropBankPipe
from src.readers.coreference import CoReferenceContentAnnotationReader
from src.readers.named_entity import NamedEntitiesContentAnnotationReader
from src.readers.propbank import PropBankContentAnnotationReader, PropBankMergedFormatAnnotationReader

# Define the pipeline
pipe_line = [
    PropBankPipe(PropBankMapping()),
    NamedEntitiesPipe(NamedEntitiesMapping(), phrase_normalizer=RestletPhraseNormalizer()),
    CoReferencePipe()
]

# The magic
triplet_list: typing.List[IContainer] = []
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
    triplet.print(f, False)
    if triplet.has_co_reference_entry:
        with_co_reference += 1
    if triplet.has_named_entities_entry:
        with_named_entities += 1

if False:
    f.write("\r\n======= Statistics:\r\n")
    f.write(f"Total PropBank entries: {total}\r\n")
    f.write(f"Entries matched with named entities: {with_named_entities}\r\n")
    f.write(f"Entries matched with co references: {with_co_reference}\r\n")
f.close()
