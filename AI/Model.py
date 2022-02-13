import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os


# Tensorflow utilities, ensures the GPU is used
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.compat.v1.Session(config=config)
sess.as_default()


# Wraps a keras/tf RNN with user interface
class ModelLSTM:
    
    def __init__(self, text):
    
        
        print("Vectorizing text sequence...")
        self.subseq_length = 60
    
        step = 3

        # unique_chars is a list of unique characters in the argument 'text'
        self.unique_chars = sorted(list(set(text)))
        # char_indices maps each char to its corresponding index in unique_chars
        self.char_indices = dict((char, self.unique_chars.index(char)) for char in self.unique_chars)
        
        # this next part splits the argument 'text' into a series of text subsequences ('raw_subseqs')
        # 'step' is the distance between each subsequence
        # so the first subsequence will be the first subseq_length characters in 'text'
        # the second subsequence will be the subseq_length character starting at index step
        # the third subsequence will be the subseq_length characters starting at index 2 * step
        
        # 'raw_target_chars' is the character that follows each subsequence of the same index in 'raw_subseqs'
        # so if subseq_length = 60, raw_subseqs[0] will be characters at indices 0 to 59 (incl) of text
        # and raw_target_chars[0] will be the char at index 60 of text
        # the reason for this is that the model will take subseq_length chars as input and predict the following character
        
        # in summary:
        # model takes in preceding sequence of subseq_length characters
        # and is trained to predict the following target char at the subseq_length + 1 position
        raw_subseqs = []
        raw_target_chars = []

        for i in range(0, len(text) - self.subseq_length, step):
            raw_subseqs.append(text[i : i + self.subseq_length])
            raw_target_chars.append(text[i + self.subseq_length])

        # one-hot encoding
        # this extends raw_subseqs and raw_target_chars by one dimension of size self.unique_chars
        # so that each character will be replaced with an array containing a single 1 (with the rest zeros)
        # and the index of that 1 corresponds with the char at the same index of unique_chars
        self.subseqs = np.zeros((len(raw_subseqs), self.subseq_length, len(self.unique_chars)), dtype=np.bool)
        self.target_chars = np.zeros((len(raw_subseqs), len(self.unique_chars)), dtype=np.bool)
        
        for subseq_index, subseq in enumerate(raw_subseqs):
            self.target_chars[subseq_index, self.char_indices[raw_target_chars[subseq_index]]] = 1
            for char_index, char in enumerate(subseq):
                self.subseqs[subseq_index, char_index, self.char_indices[char]] = 1
            
        print("Text vectorization done. Compiling model...")
        self.init_model()
          
            
    # following initialization method
    # separated to have text vectorization and keras calls in separate methods
    def init_model(self):
        self.model = keras.models.Sequential()
        self.model.add(layers.LSTM(128, input_shape=(self.subseq_length, len(self.unique_chars))))
        # output layer: a list of probabilities of length len(self.unique_chars)
        self.model.add(layers.Dense(len(self.unique_chars), activation='softmax'))
        optimizer = keras.optimizers.RMSprop(lr=0.01)

        self.callbacks = [
            # prevents an exploding gradient issue from destroying model accuracy
            keras.callbacks.EarlyStopping(monitor='acc', patience=4),
            # keras.callbacks.ModelCheckpoint(filepath="my_models/best.h5", monitor='loss', save_best_only=True),
            # halves the learning rate when there is a plateau in change of model loss,
            # allowing for smaller changes
            keras.callbacks.ReduceLROnPlateau(monitor='loss', factor= 0.5, patience=1)]
        
        self.model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['acc'])
        
        print("Model compilation finished. Call yourInstanceHere.train() to train the model.")
                
        
    # takes 'epochs' arg which is the # of epochs to train the model (if running w/ no GPU, 100+ epochs can take very long)
    def train(self, epochs=100):
        self.model_history = self.model.fit(self.subseqs, self.target_chars, batch_size=128, callbacks=self.callbacks, epochs=epochs)
        
    # This method will increase the amount of noise in the prediction list provided by the model, then return its prediction
    # The purpose of doing this: if the review generator always picks the character with the highest probability,
    # the sequences generated will be more predictable. For example: "This is a movie and this is a movie one of the best and this is a movie..."
    # But if we increase the noise, some of the less probable options will be selected in the multinomial call
    # So this method increases noise, then selects a prediction from the list of probabilities at random and returns the index of the selected
    def sample_index(self, prediction, randomness):
        prediction = np.asarray(prediction).astype('float64')
        # introduce noise into prediction
        prediction = np.log(prediction) / randomness
        prediction = np.exp(prediction) / np.sum(np.exp(prediction))
        # returns index of selected value from modified probability distribution
        return np.argmax(np.random.multinomial(1, prediction, 1))
    
    
    # generates a text review, takes args 'text_seed', 'randomness', and 'length'
    # 'text_seed' is the seed that is extended/shortened to be of length 'subseq_length'
    # these subseq_length characters are used to predict the following character,
    # which is appended onto text_seed[1:]. Then the next character is predicted etc
    # 'randomness' is the randomness variable passed into the sample_index call
    # a lower randomness (less than 0.4) tends to be more predictable and repetitive
    # a higher randomness tends to be more chaotic and have more mispellings
    # length is the number of character predictions to make
    def generate_review(self, text_seed="this was a good movie. ",  randomness=0.4, length=700):
        
        # forcing text_seed to be same length as subseq_length
        if len(text_seed) < self.subseq_length:
            text_seed = ' ' * (self.subseq_length - len(text_seed)) + text_seed
        elif len(text_seed) > self.subseq_length:
            text_seed = text_seed[-self.subseq_length:]
            
        text_seed = text_seed.lower()
        original_text_seed = text_seed
        # this variable saves all of the generated characters in sequence outside of the look
        review = ""
        i = 1

        for i in range(1, length + 1):
            seed_sample = np.zeros((1, len(text_seed), len(self.unique_chars)))
            for i, char_index in enumerate(text_seed):
                # more one-hot encoding
                seed_sample[0, i, self.char_indices[char_index]] = 1

            prediction = self.model.predict(seed_sample, verbose=0)[0]

            new_char = self.unique_chars[self.sample_index(prediction, randomness=randomness)]

            text_seed = text_seed + new_char
            text_seed = text_seed[1:]

            review = review + new_char
            if new_char == '.' and i > 500:
                break;
            
        return original_text_seed + review
    
    # helper function used in testing
    def save_model(self, file_name):
        if not os.path.exists("models"):
            os.makedirs("models")
        self.model.save("models/" + file_name)
        
