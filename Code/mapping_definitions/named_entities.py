import typing

from Code.container import TripletContainer
from Code.delegates import ChunkDelegate
from Code.words.base import IWord


def person_chunk_action(pipe, root_id: str, chunk: typing.List[IWord], container: TripletContainer,
                        default_mapping: str = None):

    container.update_instance_value(root_id, 'person')
    name_id = container.get_generated_id()
    container.add_instance(root_id, name_id, 'name', 'name')

    for i in range(len(chunk)):
        container.add(name_id, f"op{i}", f"\"{chunk[i].lemma}\"")


def joined_location_action(pipe, root_id: str, chunk: typing.List[IWord], container: TripletContainer,
                           default_mapping: str = None):

    container.update_instance_value(root_id, default_mapping)
    name_id = container.get_generated_id()
    container.add_instance(root_id, name_id, "name", "name")

    # ToDo: form or lemma? Form makes the joined phrases unreadable.
    name = ' '.join(x.form for x in chunk)
    if not (name[0] == "\"" and name[len(name)-1] == "\""):
        name = f"\"{name}\""

    container.add(name_id, f"op1", name)