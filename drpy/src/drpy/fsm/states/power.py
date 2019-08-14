from drpy.fsm.states.base import BaseState


class Exit(BaseState):

    def on_event(self, *args, **kwargs):
        raise SystemExit


class Reboot(BaseState):

    def on_event(self, *args, **kwargs):
        self.reboot()


class PowerOff(BaseState):

    def on_event(self, *args, **kwargs):
        self.power_off()
