from drpy.fsm.states.base import BaseState


class Exit(BaseState):

    def on_event(self, *args, **kwargs):
        raise SystemExit
