class ConversationMemory:
    def __init__(self):
        self.last_intent = None

    def update_intent(self, intent: dict):
        self.last_intent = intent

    def get_last_intent(self):
        return self.last_intent
