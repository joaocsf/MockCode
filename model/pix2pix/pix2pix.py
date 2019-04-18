from __future__ import print_function, division
import scipy

from keras.datasets import mnist
from keras_contrib.layers.normalization.instancenormalization import InstanceNormalization
from keras.layers import Input, Dense, Reshape, Flatten, Dropout, Concatenate
from keras.layers import BatchNormalization, Activation, ZeroPadding2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import UpSampling2D, Conv2D
from keras.models import Sequential, Model
from keras.optimizers import Adam
import datetime
import matplotlib.pyplot as plt
import sys
from .data_loader import DataLoader
import numpy as np
import os
import argparse

WORKING_DIR = os.path.dirname(__file__)

class Pix2Pix():
  def __init__(self, train_file, validation_file):
    # Input shape
    self.img_rows = 512
    self.img_cols = 512
    self.channels = 3
    self.weights_path = os.path.join(WORKING_DIR,'./weights')
    self.img_shape = (self.img_rows, self.img_cols, self.channels)
    self.train_file = train_file
    self.validation_file = validation_file
    # Configure data loader
    self.data_loader = DataLoader(train_file=self.train_file, 
                    validation_file=self.validation_file,
                    img_res=(self.img_rows, self.img_cols))


    # Calculate output shape of D (PatchGAN)
    patch = int(self.img_rows / 2**4)
    self.disc_patch = (patch, patch, 1)

    # Number of filters in the first layer of G and D
    self.gf = 64
    self.df = 64

    optimizer = Adam(0.0002, 0.5)

    # Build and compile the discriminator
    self.discriminator = self.build_discriminator()
    self.discriminator.compile(loss='mse',
      optimizer=optimizer,
      metrics=['accuracy'])

    #-------------------------
    # Construct Computational
    #   Graph of Generator
    #-------------------------

    # Build the generator
    self.generator = self.build_generator()

    # Input images and their conditioning images
    img_A = Input(shape=self.img_shape)
    img_B = Input(shape=self.img_shape)

    # By conditioning on B generate a fake version of A
    fake_A = self.generator(img_B)

    # For the combined model we will only train the generator
    self.discriminator.trainable = False

    # Discriminators determines validity of translated images / condition pairs
    valid = self.discriminator([fake_A, img_B])

    self.combined = Model(inputs=[img_A, img_B], outputs=[valid, fake_A])
    self.combined.compile(loss=['mse', 'mae'],
                loss_weights=[1, 100],
                optimizer=optimizer)
    
    self.load()

  def build_generator(self):
    """U-Net Generator"""

    def conv2d(layer_input, filters, f_size=4, bn=True):
      """Layers used during downsampling"""
      d = Conv2D(filters, kernel_size=f_size, strides=2, padding='same')(layer_input)
      d = LeakyReLU(alpha=0.2)(d)
      if bn:
        d = BatchNormalization(momentum=0.8)(d)
      return d

    def deconv2d(layer_input, skip_input, filters, f_size=4, dropout_rate=0):
      """Layers used during upsampling"""
      u = UpSampling2D(size=2)(layer_input)
      u = Conv2D(filters, kernel_size=f_size, strides=1, padding='same', activation='relu')(u)
      if dropout_rate:
        u = Dropout(dropout_rate)(u)
      u = BatchNormalization(momentum=0.8)(u)
      u = Concatenate()([u, skip_input])
      return u

    # Image input
    d0 = Input(shape=self.img_shape)

    # Downsampling
    d1 = conv2d(d0, self.gf, bn=False)
    d2 = conv2d(d1, self.gf*2)
    d3 = conv2d(d2, self.gf*4)
    d4 = conv2d(d3, self.gf*8)
    d5 = conv2d(d4, self.gf*8)
    d6 = conv2d(d5, self.gf*8)
    d7 = conv2d(d6, self.gf*8)

    # Upsampling
    u1 = deconv2d(d7, d6, self.gf*8)
    u2 = deconv2d(u1, d5, self.gf*8)
    u3 = deconv2d(u2, d4, self.gf*8)
    u4 = deconv2d(u3, d3, self.gf*4)
    u5 = deconv2d(u4, d2, self.gf*2)
    u6 = deconv2d(u5, d1, self.gf)

    u7 = UpSampling2D(size=2)(u6)
    output_img = Conv2D(self.channels, kernel_size=4, strides=1, padding='same', activation='tanh')(u7)

    return Model(d0, output_img)

  def build_discriminator(self):

    def d_layer(layer_input, filters, f_size=4, bn=True):
      """Discriminator layer"""
      d = Conv2D(filters, kernel_size=f_size, strides=2, padding='same')(layer_input)
      d = LeakyReLU(alpha=0.2)(d)
      if bn:
        d = BatchNormalization(momentum=0.8)(d)
      return d

    img_A = Input(shape=self.img_shape)
    img_B = Input(shape=self.img_shape)

    # Concatenate image and conditioning image by channels to produce input
    combined_imgs = Concatenate(axis=-1)([img_A, img_B])

    d1 = d_layer(combined_imgs, self.df, bn=False)
    d2 = d_layer(d1, self.df*2)
    d3 = d_layer(d2, self.df*4)
    d4 = d_layer(d3, self.df*8)

    validity = Conv2D(1, kernel_size=4, strides=1, padding='same')(d4)

    return Model([img_A, img_B], validity)

  def train(self, epochs, batch_size=100, sample_interval=50):

    start_time = datetime.datetime.now()

    # Adversarial loss ground truths
    valid = np.ones((batch_size,) + self.disc_patch)
    fake = np.zeros((batch_size,) + self.disc_patch)

    for epoch in range(epochs):
      print('\r Epoch %d BatchSize:%d' % (epoch, batch_size), flush=True)
      for batch_i, (imgs_A, imgs_B) in enumerate(self.data_loader.load_batch(batch_size)):

        # ---------------------
        #  Train Discriminator
        # ---------------------
        # Condition on B and generate a translated version
        fake_A = self.generator.predict(imgs_B)

        # Train the discriminators (original images = real / generated = Fake)
        d_loss_real = self.discriminator.train_on_batch([imgs_A, imgs_B], valid)
        d_loss_fake = self.discriminator.train_on_batch([fake_A, imgs_B], fake)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        # -----------------
        #  Train Generator
        # -----------------
        # Train the generators
        g_loss = self.combined.train_on_batch([imgs_A, imgs_B], [valid, imgs_A])

        elapsed_time = datetime.datetime.now() - start_time
        # Plot the progress
        print ("\r[Epoch %d/%d] [Batch %d/%d] [D loss: %f, acc: %3d%%] [G loss: %f] time: %s" % (epoch, epochs,
                                    batch_i, self.data_loader.n_batches,
                                    d_loss[0], 100*d_loss[1],
                                    g_loss[0],
                                    elapsed_time), flush=True, end='')

        # If at save interval => save generated image samples
        if batch_i % sample_interval == 0:
          self.store(epoch, batch_i, g_loss[0], 100*d_loss[1])
          self.sample_images(epoch, batch_i)

  def sample_images(self, epoch, batch_i):
    os.makedirs('images/sample/', exist_ok=True)
    r, c = 3, 3

    imgs_A, imgs_B = self.data_loader.load_data(batch_size=3, is_testing=True)
    fake_A = self.generator.predict(imgs_B)

    gen_imgs = np.concatenate([imgs_B, fake_A, imgs_A])

    # Rescale images 0 - 1
    gen_imgs = 0.5 * gen_imgs + 0.5

    titles = ['Condition', 'Generated', 'Original']
    fig, axs = plt.subplots(r, c)
    cnt = 0
    for i in range(r):
      for j in range(c):
        axs[i,j].imshow(gen_imgs[cnt])
        axs[i, j].set_title(titles[i])
        axs[i,j].axis('off')
        cnt += 1
    fig.savefig("images/sample/%d_%d.png" % (epoch, batch_i))
    plt.close()
  
  def predict_image(self, in_image):
    images = self.data_loader.convert(in_image)
    result_image = self.generator.predict(images)
    return result_image[0]

  def load(self):
    path = os.path.join(self.weights_path, 'combined_weights.h5')
    if not os.path.isfile(path): return
    print('Loading Weights...', flush=True)
    
    self.load_weights(self.discriminator, 'discriminator')
    self.load_weights(self.generator, 'generator')
    self.load_weights(self.combined, 'combined')

  def load_weights(self, model, name):
    path = os.path.join(self.weights_path, '{0}_weights.h5'.format(name))
    model.load_weights(path)

  def store(self, epoch, batch, g_loss, acc):
    self.store_weights(self.discriminator, 'discriminator', epoch, batch, g_loss, acc)
    self.store_weights(self.generator, 'generator', epoch, batch, g_loss, acc)
    self.store_weights(self.combined, 'combined', epoch, batch, g_loss, acc)

  def store_weights(self, model, name, epoch, batch, g_loss, acc):
    path1 = os.path.join(self.weights_path, '{0}_weights.h5'.format(name))
    #path2 = os.path.join(self.weights_path, 'log_ep{3}_{4}_{0}_weights_loss{1}_acc{2}.h5'.format(name, int(g_loss), int(acc), epoch, batch))
    model.save_weights(path1)
    #model.save_weights(path2)

def arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', dest='validation')
  parser.add_argument('-t', dest='train')

  return parser.parse_args()


if __name__ == '__main__':
  args = arguments()
  gan = Pix2Pix(args.train, args.validation)
  gan.train(epochs=200, batch_size=2, sample_interval=200)
