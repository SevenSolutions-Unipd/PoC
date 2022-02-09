from chatterbot.conversation import Statement
from chatterbot.logic import LogicAdapter
from server.workingHoursRequest import WorkingHoursRequest
import requests


class WorkingHoursAdapter(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.prev_statement: str = None
        self.adapter: str = None
        self.request = None
        self.apiKey: str = "d7918028-8a60-4138-8319-a29b7d75c647"

    def can_process(self, statement):
        if self.adapter is not None:
            return True

        hoursWords = ['ore', 'numero di ore']
        workWords = ['consuntivato', 'registrato', 'fatto', 'consuntivate', 'fatte']

        if not any(statement.text.lower().find(check) > -1 for check in hoursWords):
            return False

        if not any(statement.text.lower().find(check) > -1 for check in workWords):
            return False

        return True

    def process(self, input_statement, additional_response_selection_parameters):
        if self.adapter is None:
            self.adapter = "WorkingHoursAdapter"
            self.request = WorkingHoursRequest()
            self.prev_statement = None

        # if apiKey is not None:
        #     self.apiKey = apiKey

        response = self.request.parseUserInput(input_statement.text, self.prev_statement)
        response
        self.prev_statement = response

        if self.request.isReady():
            url = "https://apibot4me.imolinfo.it/v1/projects/" + self.request.project + "/activities/me"

            params = dict()
            if self.request.fromdate is not None:
                params['from'] = self.request.fromdate

            if self.request.todate is not None:
                params['to'] = self.request.todate

            responseUrl = requests.get(url, headers={"api_key": self.apiKey}, params=params)

            response_statement = Statement(self.request.parseResult(responseUrl))
            response_statement.confidence = 0

            self.adapter = None
            self.request = None
            self.prev_statement = None
        else:
            if self.request.isQuitting:
                self.adapter = None
                self.request = None
                self.prev_statement = None

            response_statement = Statement(response)
            response_statement.confidence = 0

        return response_statement
