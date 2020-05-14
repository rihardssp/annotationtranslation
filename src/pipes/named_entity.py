import logging
import typing

from src.configuration import config_reader
from src.container.base import IContainer, ContainerStatistic, stat_incr
from src.external.phrase_normalizer import IPhraseNormalizer
from src.mapping_defaults.named_entity import INamedEntitiesMapping
from src.pipes.base import PipeBase
from src.readers.named_entity import INamedEntitiesAnnotationReaderBase, NamedEntitiesFilesAnnotationReader
from src.sentences.named_entity import INamedEntitiesWord


class NamedEntitiesPipe(PipeBase):
    """Reads named entities files and matches them with existing sentences. When matched, adds as many iob format chunks to container
    and joins chunk parts if necessary"""

    def __init__(self, mapping: INamedEntitiesMapping, annotation_reader: INamedEntitiesAnnotationReaderBase = None,
                 phrase_normalizer: IPhraseNormalizer = None):
        super().__init__()
        self.phrase_normalizer: IPhraseNormalizer = phrase_normalizer
        self.mapping = mapping
        self.annotation_reader: INamedEntitiesAnnotationReaderBase = annotation_reader if annotation_reader is not None \
            else NamedEntitiesFilesAnnotationReader(config_reader.get_named_entities_resource_folder_path())
        self.__logger = logging.getLogger(config_reader.get_logger_name("NamedEntitiesPipe"))

    def _process_amr(self, container_list: typing.List[IContainer]) -> typing.List[IContainer]:
        """Checks if container list has given sentence. If so,
        separate words by chunks and proceed to mapping_definitions"""
        for sentence in self.annotation_reader.read():

            # ToDo: improve sent_id matching so that it isn't O(nm)
            potential_containers = list(x for x in container_list if x.sent_id == sentence.sent_id)
            if len(potential_containers) > 0:
                container = potential_containers[0]
                container.set_stat(ContainerStatistic.HAS_NAMED_ENTITIES, True)
                container.set_stat(ContainerStatistic.NAMED_ENTITIES_TOTAL_COUNT, sentence.bio1_count)
                container.set_stat(ContainerStatistic.NAMED_ENTITIES_COUNT, 0)
                container.set_stat(ContainerStatistic.WIKI_TOTAL_COUNT, sentence.wiki1_count)
                container.set_stat(ContainerStatistic.WIKI_COUNT, 0)

                # Last chunk
                last_chunk: typing.List[INamedEntitiesWord] = []
                container_word_ids = []
                for word in sentence.bio1:
                    # ToDo: exclude punctuation?
                    if word.bio_tag1[0] == 'B':
                        self.map_bio1_chunk(container, last_chunk, container_word_ids)
                        last_chunk = [word]
                        container_word_ids = []
                    elif word.bio_tag1[0] == 'I':
                        last_chunk.append(word)

                    if container.has_instance(word.id):
                        container_word_ids.append(word.id)

                self.map_bio1_chunk(container, last_chunk, container_word_ids)

        return container_list

    def map_bio1_chunk(self, container: IContainer, chunk: typing.List[INamedEntitiesWord],
                       container_word_ids: typing.List[str]):
        """Mapping happening here. All wiki from chunk are used on newly created instance in mapping_definitions"""

        if len(container_word_ids) == 0:
            return

        # Category is the same for every chunk item
        chunk_category = chunk[0].bio_tag1.split('-')[1]
        if chunk_category not in self.mapping.get_iob_action_mapping():
            self.__logger.info(f"chunk category '{chunk_category}' not recognised, perhaps mappings need update?")
            return

        container.update_stat(ContainerStatistic.NAMED_ENTITIES_COUNT, stat_incr)

        # Merge the words of chunk into a single instance
        for container_word_id in range(1, len(container_word_ids)):
            container.replace_instance(container_word_ids[container_word_id], container_word_ids[0])

        # Evaluate the mapping_definitions action
        mapping_action = self.mapping.iob_action_mapping[chunk_category]
        mapping_action.evaluate(self, container_word_ids[0], chunk, container)

        # After dealing with how to format chunk, we know the word the wiki refers to
        for word in chunk:
            if word.wiki1:
                container.update_stat(ContainerStatistic.WIKI_COUNT, stat_incr)
                container.add(container_word_ids[0], 'wiki', f"\"{word.wiki1}\"")