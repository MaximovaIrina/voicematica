
import numpy as np
import warnings
import torch
warnings.filterwarnings("ignore")

class VoiceMaticaRu:
    MODEL   = "microsoft/speecht5_tts"              # https://huggingface.co/microsoft/speecht5_tts
    VOCODER = "microsoft/speecht5_hifigan"          # https://huggingface.co/microsoft/speecht5_tts
    ENCODER = "speechbrain/spkrec-xvect-voxceleb"   # https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors
    SYNTHESIZER = args.syn_model_dir.joinpath("taco_pretrained")   # https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors

    def __init__(self):        
        encoder.load_model(self.MODEL)
        vocoder.load_model(self.VOCODER)
        self.synthesizer = Synthesizer(self.SYNTHESIZER, low_mem=False)
    
    def __call__(self, text, file):
        with torch.no_grad():
            preprocessed_wav = encoder.preprocess_wav(file)
            embed = encoder.embed_utterance(preprocessed_wav)
            
            texts = g2p([text, ])
            specs = synthesizer.synthesize_spectrograms(texts, [embed, ])
            spec = specs[0]
            
            generated_wav = vocoder.infer_waveform(spec)
            generated_wav = np.pad(generated_wav, (0, 16000), mode="constant")
            return generated_wav.numpy()
        

if __name__ == "__main__":
    import soundfile as sf

    vm = VoiceMaticaRu()
    
    speech = vm("Привет, моя собака милая!", "prompts_ru/762583084.ogg")
    sf.write("outputs/762583084.wav", speech, 16000)
    
    speech = vm("Привет, моя собака милая!", "prompts_ru/test.wav")
    sf.write("outputs/test_out.wav", speech, 16000)
    
    speech = vm("Привет, моя собака милая!", "prompts_ru/male.pt")
    sf.write("outputs/test_man_out.wav", speech, 16000)
    
    speech = vm("Привет, моя собака милая!", "prompts_ru/female.pt")
    sf.write("outputs/test_woman_out.wav", speech, 16000)