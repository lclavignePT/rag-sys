import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"GPU está disponível! Dispositivo: {device}")
    print(f"Nome da GPU: {torch.cuda.get_device_name(0)}") # Pega o nome da primeira GPU
else:
    device = torch.device("cpu")
    print("GPU não está disponível, usando CPU.")

print(f"Dispositivo atual: {device}")