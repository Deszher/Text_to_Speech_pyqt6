import subprocess
import torchaudio
from one_shot_talking_face.test_script import parse_phoneme_file, test_with_input_audio_and_image

PHONEME_JK = '[.w[]|{word: (.t | ascii_upcase | sub("<S>"; "sil") | sub("<SIL>"; "sil") | sub("\\(2\\)"; "") | sub("\\(3\\)"; "") | sub("\\(4\\)"; "") | sub("\\[SPEECH\\]"; "SIL") | sub("\\[NOISE\\]"; "SIL")), phones: [.w[]|{ph: .t | sub("\\+SPN\\+"; "SIL") | sub("\\+NSN\\+"; "SIL"), bg: (.b*100)|floor, ed: (.b*100+.d*100)|floor}]}]',
# pocketsphinx -phone_align yes single /content/audio.wav "Can you give me cup of tea please" \
    #     | jq '[.w[]|{word: (.t | ascii_upcase | sub("<S>"; "sil") | sub("<SIL>"; "sil") | sub("\\(2\\)"; "") | sub("\\(3\\)"; "") | sub("\\(4\\)"; "") | sub("\\[SPEECH\\]"; "SIL") | sub("\\[NOISE\\]"; "SIL")), phones: [.w[]|{ph: .t | sub("\\+SPN\\+"; "SIL") | sub("\\+NSN\\+"; "SIL"), bg: (.b*100)|floor, ed: (.b*100+.d*100)|floor}]}]' > /content/test.json

def convert_audio_to_16k(input_path: str) -> str:
    output_path = input_path[:-4] + "_16k.wav"

    waveform, sample_rate = torchaudio.load(input_path, backend="sox")
    torchaudio.save(output_path, waveform, 16000, encoding="PCM_S", bits_per_sample=16)

    return output_path

def create_phoneme(audio_path: str, text: str) -> str:
    output_path = audio_path[:-4] + "_phoneme.json"

    response= subprocess.call(
        [
            "pocketsphinx", "-phone_align", "yes", "single", "/app/"+audio_path, text,
            "|", "jq", PHONEME_JK, ">", "/app/"+output_path,
        ], 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    return output_path

def make_video(img_path: str, audio_path, phoneme_path: str) -> str:
    output_path = "data"

    generator_ckpt = "/content/checkpoint/generator.ckpt"
    audio2pose_ckpt = "/content/checkpoint/audio2pose.ckpt"

    phoneme = parse_phoneme_file(phoneme_path)
    test_with_input_audio_and_image(img_path, audio_path, phoneme, generator_ckpt, audio2pose_ckpt, output_path)

    return output_path