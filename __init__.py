# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
from mycroft.messagebus.message import Message
from mycroft import MycroftSkill, intent_handler, AdaptIntent
from threading import Lock

class QuestionsAnswersSkill(MycroftSkill):
    def __init__(self):
        super().__init__()
        self.query_replies = {}     # cache of received replies
        self.query_extensions = {}  # maintains query timeout extensions
        self.lock = Lock()

    def initialize(self):
        self.add_event('question:query.response',
                       self.handle_query_response)
        #self.register_fallback(self.handle_question, 5)


    @intent_handler(AdaptIntent().require('Question'))
    def handle_question(self, message):
        """ Send the phrase to the CommonQuerySkills and prepare for handling
            the replies.
        """
        utt = message.data.get('utterance')
        self.enclosure.mouth_think()

        self.query_replies[utt] = []
        self.query_extensions[utt] = []

        # Send the query to anyone listening for them
        self.bus.emit(Message('question:query', data={'phrase': utt}))

        self.schedule_event(self._query_timeout, 1,
                            data={'phrase': utt},
                            name='QuestionQueryTimeout')

    def handle_query_response(self, message):
        with self.lock:
            search_phrase = message.data['phrase']

            if ('searching' in message.data and
                     search_phrase in self.query_extensions):
                # Manage requests for time to complete searches
                skill_id = message.data['skill_id']
                if message.data['searching']:
                    # extend the timeout by 5 seconds
                    self.cancel_scheduled_event('QuestionQueryTimeout')
                    self.schedule_event(self._query_timeout, 7,
                                        data={'phrase': search_phrase},
                                        name='QuestionQueryTimeout')

                    # TODO: Perhaps block multiple extensions?
                    if skill_id not in self.query_extensions[search_phrase]:
                        self.query_extensions[search_phrase].append(skill_id)
                else:
                    # Search complete, don't wait on this skill any longer
                    if skill_id in self.query_extensions[search_phrase]:
                        self.query_extensions[search_phrase].remove(skill_id)
                        if not self.query_extensions[search_phrase]:
                            self.cancel_scheduled_event('QuestionQueryTimeout')
                            self.schedule_event(self._query_timeout, 0,
                                                data={'phrase': search_phrase},
                                                name='QuestionQueryTimeout')

            elif search_phrase in self.query_replies:
                # Collect all replies until the timeout
                self.query_replies[message.data['phrase']].append(message.data)

    def _query_timeout(self, message):
        # Prevent any late-comers from retriggering this query handler
        with self.lock:
            search_phrase = message.data['phrase']
            if search_phrase in self.query_extensions:
                self.query_extensions[search_phrase] = []
            self.enclosure.mouth_reset()

            # Look at any replies that arrived before the timeout
            # Find response(s) with the highest confidence
            best = None
            ties = []
            print(self.query_replies)
            if search_phrase in self.query_replies:
                for handler in self.query_replies[search_phrase]:
                    if not best or handler['conf'] > best['conf']:
                        best = handler
                        ties = []
                    elif handler['conf'] == best['conf']:
                        ties.append(handler)

            if best:
                if ties:
                    # TODO: Ask user to pick between ties or do it automagically
                    pass

                # invoke best match
                self.speak(best['answer'])
                self.log.info('Handling with: ' + str(best['skill_id']))
                self.bus.emit(Message('question:action',
                                      data={'skill_id': best['skill_id'],
                                            'phrase': search_phrase,
                                            'callback_data':
                                            best.get('callback_data')}))
            else:
                self.speak_dialog('noAnswer', data={'phrase': search_phrase})

            if search_phrase in self.query_replies:
                del self.query_replies[search_phrase]
            if search_phrase in self.query_extensions:
                del self.query_extensions[search_phrase]


def create_skill():
    return QuestionsAnswersSkill()
