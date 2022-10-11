import torch
import os
from torch.utils.data import DataLoader
import torch.optim as optim
from gen_font_data import TextDataset
from model import FontClassifier
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

FILE_TEXT = "./SRNet-Datagen/Synthtext/data/texts.txt"
FONT_DIR = "./fonts"
FONT_FILE = "./fonts/font_list.txt"

epochs = 10
global_step = 0

train_dataset = TextDataset(FILE_TEXT, FONT_DIR, FONT_FILE, train=True)
test_dataset = TextDataset(FILE_TEXT, FONT_DIR, FONT_FILE, train=False)

num_classes = 206
model = FontClassifier(1, num_classes).to(device)
for p in model.parameters():
    p.requires_grad = True
optimizer = optim.Adam(model.parameters(), lr=0.01)

train_dataloader = DataLoader(train_dataset, batch_size=128, shuffle=False)
test_dataloader = DataLoader(test_dataset, batch_size=64, shuffle=False)

loss_func = torch.nn.CrossEntropyLoss()

for epoch in range(epochs):
    print("Training...")
    model.train()
    for p in model.parameters():
        p.requires_grad = True
    pbar = tqdm(train_dataloader)
    pbar.set_description(f"Epoch {epoch}/{epochs}")
    total_loss = 0.
    cnt = 0
    for img, target in pbar:
        global_step += 1
        optimizer.zero_grad()
        print(torch.max(img))
        print(torch.min(img))
        img = img.float().to(device)
        target = target.to(device)
        pred = model(img)

        # target = torch.nn.functional.one_hot(label, num_classes)
        # target = target.float()
        loss = loss_func(pred, target)

        loss.backward()
        total_loss += loss.item()
        cnt += 1
        pbar.set_postfix({
            "loss": total_loss/cnt
        })
        optimizer.step()

    print("Evaluating...")
    pbar = tqdm(test_dataloader)
    model.eval()
    total_loss = 0.
    cnt = 0
    for img, target in pbar:
        img = img.float()
        img = img.float().to(device)
        target = target.to(device)
        pred = model(img)

        # target = torch.nn.functional.one_hot(label, num_classes)
        loss = loss_func(pred, target)
        total_loss += loss.item()
        cnt += 1
        pbar.set_postfix({
            "loss": loss.item()
        })

    print("Eval loss:", total_loss/cnt)
    torch.save({
        "model": model.state_dict(),
        "optim": optimizer.state_dict(),
        "global_step": global_step,
    }, os.path.join("/content/drive/MyDrive/Text-Replacement/checkpoints", f"{global_step}.pth"))
