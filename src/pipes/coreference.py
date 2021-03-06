import typing
from src.configuration import config_reader
from src.container.base import IContainer, ContainerStatistic, stat_incr
from src.mapping_defaults.coreference import ICoReferenceMapping, CoReferenceMapping
from src.pipes.base import PipeBase
from src.readers.coreference import ICoReferenceAnnotationReaderBase, CoReferenceFilesAnnotationReader


class CoReferencePipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding
    some things from underlying treebank """

    def __init__(self, mapping: ICoReferenceMapping = None, annotation_reader: ICoReferenceAnnotationReaderBase = None):
        super().__init__()
        self.mapping = mapping if mapping is not None else CoReferenceMapping()
        self.annotation_reader: ICoReferenceAnnotationReaderBase = annotation_reader if annotation_reader is not None \
            else CoReferenceFilesAnnotationReader(config_reader.get_co_reference_resource_folder_path(), False)

    def _process_amr(self, container_list: typing.List[IContainer]) -> typing.List[IContainer]:
        for sentence in self.annotation_reader.read():

            # ToDo: improve sent_id matching so that it isn't O(nm)
            # This co reference has a match
            potential_container = next((x for x in container_list if x.text == sentence.text), None)
            if not potential_container:
                continue

            container = potential_container
            container.set_stat(ContainerStatistic.HAS_COREFERENCE, True)
            container.set_stat(ContainerStatistic.COREFERENCE_TOTAL_COUNT, sentence.co_reference_count)
            container.set_stat(ContainerStatistic.COREFERENCE_COUNT, 0)

            for name, group in sentence.co_references.items():

                # Not all group members may be in container
                members_to_keep = []
                non_members_to_keep = []
                members_to_coreference = []

                # Separate words into groups (to keep, to co reference, to insert into container if possible)
                for group_word in group:

                    # word not in container - can't remove or co reference
                    if container.has_instance(group_word.id):

                        # the mapping defines which words NOT to keep
                        if group_word.pos_value[0:2] not in self.mapping.get_replaceable_pos_values():
                            members_to_keep.append(group_word)
                        else:
                            members_to_coreference.append(group_word)

                    elif group_word.pos_value[0:2] not in self.mapping.get_replaceable_pos_values():
                        non_members_to_keep.append(group_word)

                # in case there is some additional context for our coreference group
                if name in sentence.additional_context_references:
                    for context_group_words in sentence.additional_context_references[name]:
                        if context_group_words.pos_value[0:2] not in self.mapping.get_replaceable_pos_values():
                            non_members_to_keep.append(context_group_words)

                is_reference_added = False
                last_member_to_keep = None
                last_member_to_coreference = None

                # join all references that we want to get rid of
                if len(members_to_coreference) > 0:
                    for reference in range(1, len(members_to_coreference)):
                        container.replace_instance(members_to_coreference[reference].id, members_to_coreference[0].id)
                        container.update_stat(ContainerStatistic.SENTENCE_TOKEN_REMOVED_COUNT, stat_incr)
                        is_reference_added = True

                    last_member_to_coreference = members_to_coreference[0]

                # join all references that we want to keep (to one specific value)
                if len(members_to_keep) > 0:
                    for reference in range(1, len(members_to_keep)):
                        container.replace_instance(members_to_keep[reference].id, members_to_keep[0].id)
                        container.update_stat(ContainerStatistic.SENTENCE_TOKEN_REMOVED_COUNT, stat_incr)
                        is_reference_added = True

                    last_member_to_keep = members_to_keep[0]

                # simple scenario - replace with desireable word 1-1
                if last_member_to_coreference and last_member_to_keep:
                    is_reference_added = True
                    container.replace_instance(last_member_to_coreference.id, last_member_to_keep.id)
                    container.update_stat(ContainerStatistic.SENTENCE_TOKEN_REMOVED_COUNT, stat_incr)

                # update with value of first non-member desireable word 1-1
                elif last_member_to_coreference and len(non_members_to_keep) > 0 and non_members_to_keep[0].pos_value[0:1] != "p":
                    is_reference_added = True
                    # ToDo: Need to transform to base word. Perhaps querying UD somehow?
                    container.update_instance_value(last_member_to_coreference.id, non_members_to_keep[0].form)

                if is_reference_added:
                    container.update_stat(ContainerStatistic.COREFERENCE_COUNT, stat_incr)

        return container_list
