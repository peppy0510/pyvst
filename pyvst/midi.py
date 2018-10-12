from ctypes import sizeof, cast, POINTER, pointer
from .vstwrap import VstMidiEvent, VstEventTypes, VstEvent, get_vst_events_struct


def midi_data_as_bytes(note, velocity=100, type_='note_on', chan=1):
    """
    :param chan: Midi channel (those are 1-indexed)
    """
    if type_ == 'note_on':
        type_byte = b'\x90'[0]
    elif type_ == 'note_off':
        type_byte = b'\x80'[0]
    else:
        raise NotImplementedError('MIDI type {} not supported yet'.format(type_))

    if not (1 <= chan <= 16):
        raise ValueError('Invalid channel "{}". Must be in the [1, 16] range.'
                         .format(chan))
    return bytes([
        (chan - 1) | type_byte,
        note,
        velocity
    ])


def midi_note_event(note, velocity=100, channel=1, type_='note_on', delta_frames=0):
    """
    Generates a note (on or off) midi event (VstMidiEvent).

    :param note: midi note number
    :param velocity: 0-127
    :param channel: 1-16
    :param type_: "note_on" or "note_off"
    :delta_frames: In how many frames should the event happen.
    """
    note_on = VstMidiEvent(
        type=VstEventTypes.kVstMidiType,
        byte_size=sizeof(VstMidiEvent),
        delta_frames=delta_frames,
        flags=0,
        note_length=0,
        note_offset=0,
        midi_data=midi_data_as_bytes(note, velocity, type_, channel),
        detune=0,
        note_off_velocity=127,
    )
    return note_on


def wrap_vst_events(midi_events):
    """Wraps a list VstMidiEvent into a VstEvents structure."""
    p_midi_events = [pointer(x) for x in midi_events]
    p_midi_events = [cast(x, POINTER(VstEvent)) for x in p_midi_events]
    p_array = (POINTER(VstEvent) * len(midi_events))
    Struct = get_vst_events_struct(len(midi_events))
    events = Struct(
        num_events=len(midi_events),
        events=p_array(*p_midi_events)
    )
    return events
