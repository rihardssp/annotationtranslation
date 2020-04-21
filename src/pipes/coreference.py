import typing
from src.configuration import config_reader
from src.container import TripletContainer
from src.mapping_defaults.coreference import ICoReferenceMapping, CoReferenceMapping
from src.pipes.base import PipeBase
from src.readers.coreference import ICoReferenceAnnotationReaderBase, CoReferenceFileAnnotationReader


class CoReferencePipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding
    some things from underlying treebank """

    def __init__(self, mapping: ICoReferenceMapping = None, annotation_reader: ICoReferenceAnnotationReaderBase = None,  debug_mode: bool = False):
        super().__init__(debug_mode)
        self.mapping = mapping if mapping is not None else CoReferenceMapping()
        self.annotation_reader: ICoReferenceAnnotationReaderBase = annotation_reader if annotation_reader is not None \
            else CoReferenceFileAnnotationReader(config_reader.get_co_reference_resource_folder_path())

    def _process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:
        for sentence in self.annotation_reader.read():
            # ToDo: improve sent_id matching so that it isn't O(nm)
            potential_containers = list(x for x in triplet_list if x.text == sentence.text)

            # This co reference has a match
            if len(potential_containers) > 0:
                container = potential_containers[0]

                if self.debug_mode:
                    container.has_co_reference_entry = True

                for name, group in sentence.get_co_references().items():

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

                    # Standard scenario -
                    if len(members_to_keep) > 0 and len(members_to_coreference) > 0:
                        for reference in members_to_coreference:
                            container.replace_instance(reference.id, members_to_keep[0].id)

                    # If co reference outside of container - replace the first coreference and proceed
                    # ToDo: can be more than one non_member word (loop all of them for != "p" check)
                    elif len(non_members_to_keep) == 1 and non_members_to_keep[0].pos_value[0:1] != "p" and \
                            len(members_to_coreference) > 0:

                        # ToDo: refactor - need to update id aswell
                        # Replace the first co-reference instance
                        container.update_instance_value(members_to_coreference[0].id, non_members_to_keep[0].lemma)
                        member_id = members_to_coreference[0].id

                        # Link the rest to the updated instance
                        for reference in range(1, len(members_to_coreference)):
                            container.replace_instance(members_to_coreference[reference].id, member_id)

                    # There is more than one word pointing to the same thing, so we reference them to the first instance
                    elif len(members_to_coreference) > 1:
                        for reference in range(1, len(members_to_coreference)):
                            container.replace_instance(members_to_coreference[reference].id, members_to_coreference[0].id)

        return triplet_list
