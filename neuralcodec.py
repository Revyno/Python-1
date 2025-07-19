import torch
import torch.nn as nn
import numpy as np
import base64

# ===============================
# NEURAL CODEC (AUTOENCODER TEXT)
# ===============================
class NeuralCodec(nn.Module):
    def __init__(self, input_size, latent_size=32):
        super(NeuralCodec, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_size, latent_size),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_size, input_size),
            nn.Sigmoid()
        )

    def encode(self, x):
        return self.encoder(x)

    def decode(self, z):
        return self.decoder(z)

# ===============================
# UTILITAS KONVERSI
# ===============================
def text_to_tensor(text, vocab):
    one_hot = torch.zeros(len(text), len(vocab))
    for i, ch in enumerate(text):
        idx = vocab.index(ch)
        one_hot[i][idx] = 1
    return one_hot

def tensor_to_text(tensor, vocab):
    chars = []
    for row in tensor:
        idx = torch.argmax(row).item()
        chars.append(vocab[idx])
    return ''.join(chars)

# ===============================
# KOMPRESI
# ===============================
def kompresi_neural_codec(teks, model, vocab):
    tensor_input = text_to_tensor(teks, vocab)
    with torch.no_grad():
        encoded = model.encode(tensor_input)

    # Encode ke base64 string
    encoded_bytes = encoded.numpy().astype(np.float32).tobytes()
    encoded_b64 = base64.b64encode(encoded_bytes).decode('utf-8')
    return encoded_b64

# ===============================
# DEKOMPRESI
# ===============================
def dekompresi_neural_codec(encoded_b64, model, vocab):
    encoded_bytes = base64.b64decode(encoded_b64)
    encoded_array = np.frombuffer(encoded_bytes, dtype=np.float32)
    encoded_tensor = torch.tensor(encoded_array, dtype=torch.float32).reshape(-1, 32)

    with torch.no_grad():
        decoded = model.decode(encoded_tensor)

    return tensor_to_text(decoded, vocab)

# ===============================
# MAIN
# ===============================
def main():
    teks = input("Masukkan teks untuk dikompresi: ")

    # Bangun vocab
    vocab = sorted(set(teks))
    input_size = len(vocab)
    model = NeuralCodec(input_size)

    # Latih model autoencoder
    print("Tes neural codec...")
    data = text_to_tensor(teks, vocab)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    for epoch in range(300):
        optimizer.zero_grad()
        encoded = model.encode(data)
        decoded = model.decode(encoded)
        loss = criterion(decoded, data)
        loss.backward()
        optimizer.step()

    # Kompresi
    encoded_b64 = kompresi_neural_codec(teks, model, vocab)
    print("\n Teks terkompresi (base64):\n", encoded_b64)

    # Dekompresi
    hasil_dekompresi = dekompresi_neural_codec(encoded_b64, model, vocab)
    print("\n Hasil dekompresi:\n", hasil_dekompresi)

if __name__ == '__main__':
    main()
