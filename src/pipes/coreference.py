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
            else CoReferenceFilesAnnotationReader(config_reader.get_co_reference_resource_folder_path())

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
                for context_group_words in sentence.additional_context_references[name]:
                    if context_group_words.pos_value[0:2] not in self.mapping.get_replaceable_pos_values():
                        non_members_to_keep.append(context_group_words)

                is_reference_added = False

                # Standard scenario
                if len(members_to_keep) > 0 and len(members_to_coreference) > 0:
                    is_reference_added = True
                    for reference in members_to_coreference:
                        container.replace_instance(reference.id, members_to_keep[0].id)

                # If co reference outside of container - replace the first coreference and proceed
                # ToDo: update condition above instead of checking here.
                elif len(non_members_to_keep) == 1 and non_members_to_keep[0].pos_value[0:1] != "p" and \
                        len(members_to_coreference) > 0:
                    is_reference_added = True

                    # ToDo: refactor - need to update id aswell
                    # Replace the first co-reference instance
                    container.update_instance_value(members_to_coreference[0].id, non_members_to_keep[0].form)
                    member_id = members_to_coreference[0].id

                    # Link the rest to the updated instance
                    for reference in range(1, len(members_to_coreference)):
                        container.replace_instance(members_to_coreference[reference].id, member_id)

                # There is more than one word pointing to the same thing, so we reference them to the first instance
                elif len(members_to_coreference) > 1:
                    is_reference_added = True
                    for reference in range(1, len(members_to_coreference)):
                        container.replace_instance(members_to_coreference[reference].id, members_to_coreference[0].id)

                if is_reference_added:
                    container.update_stat(ContainerStatistic.COREFERENCE_COUNT, stat_incr)

        return container_list
