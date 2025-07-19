import math
from collections import defaultdict
# metode ppm (Prediction by Partial Matching) untuk kompresi teks/ metdoe markov 
# metode huffman coding
def calculate_ppm_compression(text):
    
    order0_freq = defaultdict(int)
    for char in text:
        order0_freq[char] += 1
    total_chars = len(text)
    order0_prob = {char: freq/total_chars for char, freq in order0_freq.items()}
    

    order1_freq = defaultdict(lambda: defaultdict(int))
    for i in range(len(text)-1):
        context = text[i]
        next_char = text[i+1]
        order1_freq[context][next_char] += 1
    
    order1_prob = defaultdict(dict)
    escape_prob = {}
    
    for context in order1_freq:
        total = sum(order1_freq[context].values())
        for char in order1_freq[context]:
            order1_prob[context][char] = order1_freq[context][char] / (total + 1)
        escape_prob[context] = 1 / (total + 1)
    

    total_bits = 0
    bits_per_char = []
    
    for i in range(len(text)):
        char = text[i]
        
        if i == 0:
          
            prob = order0_prob[char]
            bits = -math.log2(prob)
        else:
            context = text[i-1]
            if char in order1_prob.get(context, {}):
                prob = order1_prob[context][char]
                bits = -math.log2(prob)
            else:
              
                prob = escape_prob.get(context, 1)
                bits = -math.log2(prob)
        
        total_bits += bits
        bits_per_char.append((char, bits))
    
  
    original_bits = len(text) * 8  
    compression_ratio = (original_bits - total_bits) / original_bits * 100
    
    return {
        'original_text': text,
        'original_bits': original_bits,
        'compressed_bits': total_bits,
        'compression_ratio': compression_ratio,
        'bits_per_char': bits_per_char,
        'order0_prob': order0_prob,
        'order1_prob': dict(order1_prob),
        'escape_prob': escape_prob
    }

def main():
    print("=== Program Kompresi Teks dengan PPM ===")
    print("Masukkan teks yang ingin dikompresi (tekan Enter 2 kali untuk selesai):")
    
 
    lines = []
    while True:
        line = input()
        if line == "":
            if len(lines) > 0:  
                break
            else:
                print("Silakan masukkan teks terlebih dahulu!")
                continue
        lines.append(line)
    
    text = "\n".join(lines)
    
    if not text:
        print("Tidak ada teks yang dimasukkan!")
        return
    
    result = calculate_ppm_compression(text)
    
    
    print("\n=== Hasil Kompresi ===")
    print(f"Teks asli: {result['original_text']}")
    print(f"Total bit asli (ASCII): {result['original_bits']} bit")
    print(f"Total bit setelah kompresi PPM: {result['compressed_bits']:.2f} bit")
    print(f"Rasio kompresi: {result['compression_ratio']:.1f}% lebih efisien")

    print("\nDetail bit per karakter:")
    for i, (char, bits) in enumerate(result['bits_per_char']):
        print(f"Karakter {i+1}: '{char}' = {bits:.2f} bit")

    print("\nProbabilitas Orde-0:")
    for char, prob in result['order0_prob'].items():
        print(f"P({char}) = {prob:.3f}")

    print("\nProbabilitas Orde-1:")
    for context, probs in result['order1_prob'].items():
        for char, prob in probs.items():
            print(f"P({char}|{context}) = {prob:.3f}")
        print(f"P(ESC|{context}) = {result['escape_prob'][context]:.3f}")

if __name__ == "__main__":
    main()