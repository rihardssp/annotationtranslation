import typing
from code.configuration import config_reader
from code.container import TripletContainer
from code.pipes.base import PipeBase
from code.readers.coreference import ICoReferenceAnnotationReaderBase, CoReferenceFileAnnotationReader


class CoReferencePipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding
    some things from underlying treebank """

    def __init__(self, annotation_reader: ICoReferenceAnnotationReaderBase = None, debug_mode: bool = False):
        super().__init__(debug_mode)
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
                    members_to_coreference = []

                    for group_word in group:

                        # word not in container - can't remove or co reference
                        if container.has_instance(group_word.id):

                            # the mapping defines which words NOT to keep
                            if len(group_word.pos_value) >= 2 and group_word.pos_value[0:2] not in ("pp", "px"):
                                members_to_keep.append(group_word)
                            else:
                                members_to_coreference.append(group_word)

                    # For now only co reference if we have 1 word to keep and more than 0 to remove
                    if len(members_to_keep) == 1 and len(members_to_coreference) > 0:
                        for reference in members_to_coreference:
                            container.replace_instance(reference.id, members_to_keep[0].id)


        return triplet_list
