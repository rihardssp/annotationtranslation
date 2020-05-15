import logging
import typing
import codecs

from src.configuration import ConfigReader, config_reader

# use to log (can be displayed to user!):
# log_stream = StringIO() | stream=log_stream, datefmt='%H:%M:%S', | print(log_stream.getvalue())
logging.basicConfig(level=config_reader.get_logger_severity_level(), format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')

from src.container.base import IContainer, ContainerStatistic
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
for triplet in triplet_list:
    triplet.print(f, False)


# Some additional data
propbank_sentence_count = len(triplet_list)
with_co_reference = len(list(x for x in triplet_list if x.get_stat(ContainerStatistic.HAS_COREFERENCE, False)))
with_named_entities = len(list(x for x in triplet_list if x.get_stat(ContainerStatistic.HAS_NAMED_ENTITIES, False)))
property_count = sum(list(x.property_count for x in triplet_list))
sentence_token_count = sum(list(x.token_count for x in triplet_list))
sentence_token_total_count = sum(list(x.get_stat(ContainerStatistic.SENTENCE_TOKEN_TOTAL_COUNT, 0) for x in triplet_list))
frame_count = sum(list(x.frame_count for x in triplet_list))
frame_total_count = sum(list(x.get_stat(ContainerStatistic.FRAME_TOTAL_COUNT, 0) for x in triplet_list))
named_entities_total_count = sum(list(x.get_stat(ContainerStatistic.NAMED_ENTITIES_TOTAL_COUNT, 0) for x in triplet_list))
named_entities_count = sum(list(x.get_stat(ContainerStatistic.NAMED_ENTITIES_COUNT, 0) for x in triplet_list))
wiki_total_count = sum(list(x.get_stat(ContainerStatistic.WIKI_TOTAL_COUNT, 0) for x in triplet_list))
wiki_count = sum(list(x.get_stat(ContainerStatistic.WIKI_COUNT, 0) for x in triplet_list))
coreference_count = sum(list(x.get_stat(ContainerStatistic.COREFERENCE_COUNT, 0) for x in triplet_list))
coreference_total_count = sum(list(x.get_stat(ContainerStatistic.COREFERENCE_TOTAL_COUNT, 0) for x in triplet_list))

f.close()
f = codecs.open(ConfigReader().get_output_file_path().replace(".txt", "") + "_statistics.txt", "w", "utf-8")

f.write("======= Statistics:\n")
f.write(f"Total AMR property count: {property_count}\n")
f.write(f"AMR token count: {sentence_token_count} out of total: {sentence_token_total_count}\n")
f.write(f"PropBank frame count in AMR: {frame_count} out of total: {frame_total_count}\n")
f.write(f"Named entity count in AMR: {named_entities_count} out of total: {named_entities_total_count}\n")
f.write(f"Wiki count in AMR: {wiki_count} out of total: {wiki_total_count}\n")
f.write(f"Coreference count in AMR: {coreference_count} out of total: {coreference_total_count}\n")

f.write(f"Number of AMR graphs generated from PropBank: {propbank_sentence_count}\n")
f.write(f"Entries matched with named entities: {with_named_entities}\n")
f.write(f"Entries matched with co references: {with_co_reference}\n")

f.close()
