import gradio as gr
import os

# --- IMPORTANT: Ensure 'Backend.py' is in the same directory ---
try:
    from Backend import Podcast
except ImportError:
    raise ImportError("Cannot import 'Podcast' from 'Backend.py'. "
                      "Please ensure 'Backend.py' exists and defines the 'Podcast' class correctly.")

def generate_podcast_app_logic(pdf_file):
    """
    Handles the Gradio input, calls the backend Podcast class,
    and returns outputs for the Gradio UI.
    """
    if pdf_file is None:
        yield "❌ Please upload a PDF file.", None, None, None
        return

    # Gradio provides the path to the uploaded temporary file
    pdf_path = pdf_file.name
    
    yield "🔄 Initializing podcast generation (this may take a while)...", None, None, None
    print(f"Received PDF: {pdf_path}")

    try:
        # Instantiate your Backend Podcast class
        AI = Podcast(pdf_path) 
        
        # Call your backend method to create the podcast
        yield "🎯 Generating podcast (summarizing, creating script, synthesizing audio)...", None, None, None
        AI.createPodcast()

        # Check for generated files
        output_audio_path = 'podcast.mp3'
        script_path = 'script.txt'
        
        transcript_content = ""
        
        # Read transcript if it exists
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    transcript_content = f.read()
            except Exception as e:
                transcript_content = f"Error reading transcript: {e}"
        else:
            transcript_content = "Transcript file not found."

        if os.path.exists(output_audio_path):
            yield "✅ Podcast generated successfully!", transcript_content, output_audio_path, script_path
            print("Podcast generation complete.")
        else:
            yield "❌ Error - 'podcast.mp3' was not found after generation.", transcript_content, None, None
            print("Error: 'podcast.mp3' was not found.")

    except Exception as e:
        yield f"❌ An error occurred: {e}", "", None, None
        print(f"An error occurred during podcast generation: {e}")

# Custom CSS for a clean, professional look
custom_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #333;
        margin: 0;
        padding: 20px;
    }

    .gradio-container {
        max-width: 900px !important;
        margin: 0 auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    h1 {
        font-family: 'Inter', sans-serif;
        color: #2d3748;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
        font-size: 2.5em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .gr-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .gr-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
    }

    .gr-label {
        font-weight: 600 !important;
        color: #4a5568 !important;
        font-size: 1.1em !important;
        margin-bottom: 10px !important;
    }

    .gr-textbox, .gr-file-input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 12px 16px !important;
        transition: border-color 0.3s ease;
    }
    
    .gr-textbox:focus, .gr-file-input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    .gr-textbox textarea {
        min-height: 200px !important;
        font-family: 'Monaco', 'Consolas', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    .gr-file-input {
        background: #f7fafc !important;
        border-style: dashed !important;
    }

    .gr-audio-player {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        background: #ffffff;
        padding: 20px;
        margin-top: 20px;
        border: 2px solid #e2e8f0;
    }

    #status_output {
        font-size: 16px !important;
        font-weight: 500 !important;
        text-align: center;
        padding: 15px !important;
        border-radius: 12px !important;
        background: #f0f4f8 !important;
        border: 2px solid #e2e8f0 !important;
    }

    .upload-section {
        background: #f8fafc;
        padding: 30px;
        border-radius: 16px;
        border: 2px dashed #cbd5e0;
        margin-bottom: 30px;
        text-align: center;
    }
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft(), title="Book to Podcast Generator") as demo:
    gr.Markdown(
        """
        # 🎙️ Book to Podcast Generator
        **Transform your PDF book into an engaging conversational podcast!**
        
        Simply upload your PDF file and click generate. The AI will create both an audio podcast and a detailed transcript for you.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            pdf_upload = gr.File(
                label="📚 Upload Your Book (PDF)",
                file_types=[".pdf"],
                file_count="single",
                interactive=True,
                elem_classes=["upload-section"]
            )
            
            generate_btn = gr.Button(
                "🚀 Generate Podcast", 
                variant="primary",
                size="lg"
            )

        with gr.Column(scale=2):
            status_output = gr.Textbox(
                label="📊 Processing Status",
                interactive=False,
                elem_id="status_output",
                placeholder="Upload a PDF and click 'Generate Podcast' to begin...",
                show_copy_button=False
            )

    with gr.Row():
        with gr.Column():
            podcast_transcript = gr.Textbox(
                label="📝 Podcast Transcript",
                interactive=False,
                lines=12,
                placeholder="The generated conversation transcript will appear here...",
                show_copy_button=True
            )
            
            transcript_download = gr.File(
                label="💾 Download Transcript",
                interactive=False,
                visible=False
            )

        with gr.Column():
            podcast_audio = gr.Audio(
                label="🎧 Generated Podcast",
                type="filepath",
                interactive=False,
                show_download_button=True
            )

    # Event Handler
    generate_btn.click(
        fn=generate_podcast_app_logic,
        inputs=[pdf_upload],
        outputs=[status_output, podcast_transcript, podcast_audio, transcript_download],
        api_name="generate_podcast"
    )

    # Show download button for transcript when available
    def show_transcript_download(transcript_file):
        if transcript_file and os.path.exists(transcript_file):
            return gr.update(visible=True, value=transcript_file)
        return gr.update(visible=False)
    
    transcript_download.change(
        fn=show_transcript_download,
        inputs=[transcript_download],
        outputs=[transcript_download]
    )

if __name__ == "__main__":
    # demo.launch(
    #     server_name="0.0.0.0",  # Makes it accessible from other devices on network
    #     server_port=7860,       # Default Gradio port
    #     share=False,            # Set to True if you want a public link
    #     show_error=True,        # Shows errors in the interface
    #     show_api=False          # Hides the API documentation
    # )
    demo.launch(share=False)