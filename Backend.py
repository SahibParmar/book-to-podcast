from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import google.generativeai as genai
# from langchain_community.vectorstores import FAISS # Not used, can remove
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma, FAISS
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import asyncio
import edge_tts
from pydub import AudioSegment
import os

class Podcast:
    def __init__(self,pdf_path):
        self.pdf_path=pdf_path
        self.embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # --- Load Environment Variables ---
        load_dotenv()
        self.GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")

        if not self.GENAI_API_KEY:
            print("❌ GENAI_API_KEY not found.")
        else:
            genai.configure(api_key=self.GENAI_API_KEY)

        # === Setup Model + Memory ===
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=self.GENAI_API_KEY, 
            temperature=0.6
        )

        self.voices = {
            "male": "en-US-GuyNeural",
            "female": "en-US-JennyNeural"
        }

    def pdf_to_text(self,txt_output_path):
        # creating a pdf reader object
        reader = PdfReader(self.pdf_path)

        # printing number of pages in pdf file
        print(f"found total {len(reader.pages)} pages content!")

        # Reading pages
        text=''
        for page in reader.pages:
            text+=page.extract_text()
        with open(txt_output_path, 'w', encoding='utf-8') as f:
                f.write(text)

        return text
    
    def split_text(self,text,chunk_size=5000,chunk_overlap=300):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,     # Can go much higher for Gemini
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_text(text)
        return chunks
    
    def store_embeddings(self,chunks, store_type='chroma', persist_directory='vectorstore'):
        # You can change model_name to a better one if needed
        if store_type == 'chroma':
            self.vectordb = Chroma.from_texts(
                texts=chunks,
                embedding=self.embedder,
                persist_directory=persist_directory
            )
            self.vectordb.persist()
        elif store_type == 'faiss':
            self.vectordb = FAISS.from_texts(texts=chunks, embedding=self.embedder)
            FAISS.save_local(self.vectordb, persist_directory)
        else:
            raise ValueError("Invalid vector store type. Use 'chroma' or 'faiss'")
        return self.vectordb
    
    def get_raw_info(self):
        text = self.pdf_to_text("my_book.txt")
        self.chunks = self.split_text(text)
        self.chunks_larger = self.split_text(text,600000,chunk_overlap=300)
        self.vectordb = self.store_embeddings(self.chunks, store_type='chroma')

        author_question=f'''
        can you say author and title of the book from the chunk provided?
        Answer if you find author's name. or else just give one line summary.
        here's the chunk:
        {self.chunks[0]}
        '''

        def get_question_prompt(idx_of_chunk,basic_info=None):
            chunk=self.chunks_larger[idx_of_chunk]
            return f'''
            Hey, here I'm Providing you chunk from some book. You have to write a set of questions for podcast
            to the author of the book. provide only questions....nothing else.
            1. you have to give 3-4 line summary of the provided entire chunk.
            2. you have to give 15 good questions that will cover maximum of the concept of the provided chunk
            here's the chunk:
            {chunk}
            '''
        def generate_ai_response(prompt):
            os.system("cls")
            """Generate response using Google Gemini."""
            if not self.GENAI_API_KEY:
                print("Cannot generate AI response: GENAI_API_KEY not configured.")
                return None
            try:
                model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=self.GENAI_API_KEY, temperature=0.6) # Fallback?
                print("Generating AI response...")
                response = model.invoke(prompt)
                print("AI response received.")
                # call_count+=1
                # print(f'call number-{call_count}')
                return response
            except Exception as e:
                print(f"Error generating AI response: {e}")
                return None



        book_desc=generate_ai_response(author_question).content
        with open("desc.txt",'w') as f:
            f.write(book_desc)

        raw_questions=''
        for i in range(len(self.chunks_larger)):
            response=generate_ai_response(get_question_prompt(i,book_desc)).content
            raw_questions+=f"chunk-{i+1}\n"
            raw_questions+=response
            raw_questions+='---------------------------'

        with open("raw_que.txt",'w') as f:
            f.write(raw_questions)

        # Filtering questions and get final questions
        filtering_prompt=f'''
        I am going for a podcast where I have to talk to the author about his book.
        My main goal is to have an informational content which can cover nearly entire book with just 10-15 main core questions.
        Here I am providing you my work that I carried out on chunks ok books. I will provide summary of the chunks (what is that chunk
        of book about), and few questions from it.

        after looking at all the questions , give me filtered out 10-15 question in a proper flow (you can add some question if you want, and also delete some if you feel so)
        Note: provide only list of such filtered questions.

        here's my work:
        {book_desc}
        -----------------------------------------
        {raw_questions}
        '''
        filtered_questions=generate_ai_response(filtering_prompt).content

        with open("final.txt",'w') as f:
            f.write(filtered_questions)
        
        with open('final.txt','r', encoding='utf-8') as f: # Added encoding
            important_questions=f.read()

        # === Prompt Template for Question Extraction ===
        parser = JsonOutputParser()

        template = PromptTemplate(
            template=    """
        You are an expert editor. Your task is to extract a list of distinct questions from the provided text.
        Ensure each question is clearly separated and returned as a list of strings. Make sure text in question is clean or UTF-8 encoded.
        Questions to extract:
        ```{questions}```

        {format_instructions}
        """,
            input_variables=['questions'],
            partial_variables={'format_instructions': parser.get_format_instructions()}
        )
        chain = template | self.llm | parser
        questions = chain.invoke({'questions':important_questions})

        def search_similar_chunks(query, vectordb, top_k=3):
            """
            Performs similarity search on the stored vector DB using a query.
            Returns top_k most similar chunks.
            """
            print(f"🔍 Searching for: '{query}'")
            results = vectordb.similarity_search(query, k=top_k)

            temp=''
            for i, doc in enumerate(results):
                temp+=f"\n📚 Result {i+1}:\n{'-'*40}\n"
                temp+=doc.page_content

            return temp +'\n'
        
        my_script=f'''
        Description:
        {book_desc}
        ------------------------------

        '''
        for i,question in enumerate(questions):
            try:
                my_script+=(f"QUE-{i+1}: "+question)
                my_script+='\n'
                my_script+=search_similar_chunks(question,self.vectordb,6)
                my_script+=f'\n{'-'*50}'
                my_script+='\n\n\n\n'
            except:
                continue

        prompt = f"""
        You are a professional podcast scriptwriter.

        Your task is to convert the following rough draft — which contains a series of questions and corresponding detailed content — into a fluent, engaging, and natural-sounding podcast conversation between two hosts.

        Use this structure:
        - [Male Host]: Asks the question and reflects on it.
        - [Female Host]: Responds with insightful, expressive elaboration drawn from the content.

        Requirements:
        - DO NOT use any markdown symbols (like *, #, bullet points, etc.).
        - DO NOT repeat the question verbatim. Rephrase it in a conversational style.
        - Keep the tone friendly, emotional, and flowing — like real people speaking.
        - The response part should be more elaborative and medium long.
        - Maintain a light dynamic between the hosts while staying true to the message of the book.
        - Feel free to paraphrase and compress the original text when needed, but don’t leave out important meaning.
        - Write the entire dialogue as a single conversation.
        - This will later be converted into speech using text-to-speech, so make sure it sounds like something people would actually say aloud.

        Here is the rough content:

        {my_script}

        Now write the podcast conversation accordingly.
        """



        result=self.llm.invoke(prompt)
        # print(result.content)
        with open('script.txt','w', encoding='utf-8') as f:
            f.write(result.content)
    




    async def text_to_speech(self, text, voice, filename):
        ##cheerful  ,sad ,angry , excited , friendly , terrified , hopeful , shouting , whispering
        # ssml = f"""
        #     <speak version="1.0" xml:lang="en-US">
        #     <voice name="{voice}">
        #         <mstts:express-as style="cheerful">
        #         {text}
        #         </mstts:express-as>
        #     </voice>
        #     </speak>
        #     """
        communicate = edge_tts.Communicate(text, voice)
        # communicate = edge_tts.Communicate(ssml, voice, ssml=True)
        await communicate.save(filename)
    async def generate_podcast(self, script_path="script.txt", output_path="podcast.mp3"):
        if not os.path.exists(script_path):
            print("❌ script.txt not found!")
            return

        # Read and parse script
        with open(script_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        dialogues = self.split_by_speaker(raw_text)

        # Generate audio files and combine
        segments = []
        for i, (speaker, line) in enumerate(dialogues):
            voice = self.voices.get(speaker.lower(), self.voices["female"])
            file_name = f"temp_{i}.mp3"
            print(f"🎙️ Synthesizing line {i+1}/{len(dialogues)} ({speaker}): {line[:50]}...")
            await self.text_to_speech(line, voice, file_name)
            segments.append(AudioSegment.from_file(file_name))

        print("🎧 Merging audio segments...")
        final_audio = sum(segments)
        final_audio.export(output_path, format="mp3")
        print(f"✅ Podcast saved as {output_path}")

        # Clean temp files
        for i in range(len(segments)):
            os.remove(f"temp_{i}.mp3")
    def split_by_speaker(self,script_text):
        parts = []
        current_speaker = None
        current_lines = []

        for line in script_text.splitlines():
            if line.startswith("[Male Host]") or line.startswith("[Female Host]"):
                if current_speaker and current_lines:
                    parts.append((current_speaker, " ".join(current_lines).strip()))
                    current_lines = []
                current_speaker = "male" if "Male" in line else "female"
                current_lines.append(line.split("]:", 1)[1].strip())
            else:
                current_lines.append(line.strip())

        if current_speaker and current_lines:
            parts.append((current_speaker, " ".join(current_lines).strip()))

        return parts
    
    def speekOut(self):
        asyncio.run(self.generate_podcast("script.txt", "podcast.mp3"))
    
    def createPodcast(self):
        self.get_raw_info()
        self.speekOut()

if __name__=='__main__':
    # pdf_path='Men-are-from-mars-women-are-from-venus.pdf'
    pdf_path='jonathan-livingston-seagull.pdf'
    AI=Podcast(pdf_path)

    import time
    t1=time.time()
    AI.createPodcast()
    t2=time.time()

    print(f"Podcast created in just {t2-t1}!!")