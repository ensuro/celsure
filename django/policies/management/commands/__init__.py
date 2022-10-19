class PrintMixin:
    def _print(self, message, style="SUCCESS", stderr=False):
        if stderr:
            self.stderr.write(getattr(self.style, style)(message))
        else:
            self.stdout.write(getattr(self.style, style)(message))
