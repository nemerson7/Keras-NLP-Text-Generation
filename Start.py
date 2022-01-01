
import Model

path = input("Please enter text file path: ")
path = path.strip()
file = open(path, "r")
text = file.read()
file.close()

n_epochs = int(input("Please enter the number of epochs for training: "))
seed = input("Enter text seed: ")

model = Model.ModelLSTM(text)
model.train(epochs = n_epochs)

print("Generating reviews...")
r1 = model.generate_review(text_seed = seed)
r2 = model.generate_review(text_seed = seed)
r3 = model.generate_review(text_seed = seed)


print("\nREVIEW 1 ******************\n")
print(r1)

print("\nREVIEW 2 ******************\n")
print(r2)

print("\nREVIEW 3 ******************\n")
print(r3)



