import streamlit as st
# import pynecone as pc
from youtube_transcript_api import YouTubeTranscriptApi
import math
import textwrap
import openai
openai.api_key = st.secrets["api_key"]
import urllib.parse

def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_id(self):
    self.video_id = self.url.split("v=")[1].split('&')[0]

def in_progress(self):
    self.progress = True

def get_transcription(self):
    # Use the youtube_transcript_api library to get the transcript for the video
    transcripts = YouTubeTranscriptApi.get_transcript(self)

    # Print the transcript
    total_transcript = ""
    for transcript in transcripts:
        total_transcript += transcript["text"] + " "
    return total_transcript

def summarize(self):
    if len(self) < 16000:
        # Use the OpenAI API to generate a summary of the transcription
        prompt = ("Please give me a one sentence summary of what the following text is about:" + self)
        model_engine = "text-davinci-003"
        summary = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024, temperature=0.5)
        try:
            return summary['choices'][0]['text'].split('\n\n')[1]
        except IndexError:
            return summary['choices'][0]['text']
    else:
        seg_summaries = ""
        segment_count = math.ceil(len(self)/16000) #2048 tokens = 1500 words = 8000 characters
        per_segment = math.ceil(len(self)/segment_count)
        segmented_transcript = textwrap.wrap(self, per_segment)
        for segment in segmented_transcript:
            prompt = ("Please give me a one sentence summary of what the following text is about:" + segment)
            model_engine = "text-davinci-003"
            summary = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024, temperature=0.5)
            try:
                seg_summaries += summary['choices'][0]['text'].split('\n\n')[1] + " "
            except IndexError:
                seg_summaries += summary['choices'][0]['text'] + " "
        prompt = ("Please give me a one sentence paragraph of what the following text is about:" + seg_summaries)
        model_engine = "text-davinci-003"
        summary = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024, temperature=0.5)
        return summary['choices'][0]['text']


st.title("Youtube Summerizer")
url = st.text_input("Enter a URL")


if is_valid_url(url):
    video_id = url.split("v=")[1].split('&')[0]
    st.write("The video ID is:", video_id)
    transcript = get_transcription(video_id)
    st.write("The one sentence summary is:", summarize(transcript))
else:
    st.write("You did not enter a valid URL. Please try again.")


# class State(pc.State):
#     api: str = ""
#     url: str = ""
#     video_id: str = ""
#     transcription: str = ""
#     summary: str = ""
#     progress: bool = False

#     def get_id(self):
#         self.video_id = self.url.split("v=")[1].split('&')[0]

#     def in_progress(self):
#         self.progress = True

#     def get_transcription(self):
#         # Use the youtube_transcript_api library to get the transcript for the video
#         transcripts = YouTubeTranscriptApi.get_transcript(self.video_id)

#         # Print the transcript
#         total_transcript = ""
#         for transcript in transcripts:
#             total_transcript += transcript["text"] + " "
#         self.transcription = total_transcript

#     def summarize(self):
#         if len(self.transcription) < 16000:
#             # Use the OpenAI API to generate a summary of the transcription
#             prompt = ("Please give me a one sentence summary of what the following text is about:" + self.transcription)
#             model_engine = "text-davinci-003"
#             summary = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024, temperature=0.5)
#             try:
#                 self.summary = summary['choices'][0]['text'].split('\n\n')[1]
#             except IndexError:
#                 self.summary = summary['choices'][0]['text']
#         else:
#             seg_summaries = ""
#             segment_count = math.ceil(len(self.transcription)/16000) #2048 tokens = 1500 words = 8000 characters
#             per_segment = math.ceil(len(self.transcription)/segment_count)
#             segmented_transcript = textwrap.wrap(self.transcription, per_segment)
#             for segment in segmented_transcript:
#                 prompt = ("Please give me a one sentence summary of what the following text is about:" + segment)
#                 model_engine = "text-davinci-003"
#                 summary = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024, temperature=0.5)
#                 try:
#                     seg_summaries += summary['choices'][0]['text'].split('\n\n')[1] + " "
#                 except IndexError:
#                     seg_summaries += summary['choices'][0]['text'] + " "
#             prompt = ("Please give me a one sentence paragraph of what the following text is about:" + seg_summaries)
#             model_engine = "text-davinci-003"
#             summary = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024, temperature=0.5)
#             self.summary = summary['choices'][0]['text']
#         self.progress = False

# def index():
#     return pc.vstack(
#         pc.hstack(
#             pc.heading('Youtube URL', font_size="1em", width="100%"),
#             pc.input(
#                 on_blur=State.set_url,
#                 width="100%"
#             ),
#         ),
#         pc.button(
#             'Summarize',
#             on_click=[State.get_id, State.in_progress, State.get_transcription, State.summarize],
#         ),
#         pc.circular_progress(is_indeterminate=State.progress),
#         # pc.hstack(
#         #     pc.heading('Transcript', font_size="1em"),
#         #     pc.text(State.transcription),
#         # ),
#         pc.hstack(
#             pc.heading('Summary', font_size="1em"),
#             pc.text(State.summary),
#         ),
#     )
# # Add state and page to the app.
# app = pc.App(state=State)
# app.add_page(index)
# app.compile()
