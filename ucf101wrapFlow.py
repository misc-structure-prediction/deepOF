"""Contains a warp flow model, which adapt from vgg16 net.
"""
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np

def VGG16(inputs, outputs, loss_weight, labels):
    """
    Spatial stream based on VGG16

    """

    with slim.arg_scope([slim.conv2d, slim.fully_connected], 
                        activation_fn=tf.nn.relu,
                        weights_initializer=tf.truncated_normal_initializer(0.0, 0.01),
                        weights_regularizer=slim.l2_regularizer(0.0005)):

        # conv1_1 = slim.conv2d(tf.concat(3, [inputs, outputs]), 64, [3, 3], scope='conv1_1')
        conv1_1 = slim.conv2d(inputs, 64, [3, 3], scope='conv1_1')
        conv1_2 = slim.conv2d(conv1_1, 64, [3, 3], scope='conv1_2')
        pool1 = slim.max_pool2d(conv1_2, [2, 2], scope='pool1')

        conv2_1 = slim.conv2d(pool1, 128, [3, 3], scope='conv2_1')
        conv2_2 = slim.conv2d(conv2_1, 128, [3, 3], scope='conv2_2')
        pool2 = slim.max_pool2d(conv2_2, [2, 2], scope='pool2')

        conv3_1 = slim.conv2d(pool2, 256, [3, 3], scope='conv3_1')
        conv3_2 = slim.conv2d(conv3_1, 256, [3, 3], scope='conv3_2')
        conv3_3 = slim.conv2d(conv3_2, 256, [3, 3], scope='conv3_3')
        pool3 = slim.max_pool2d(conv3_3, [2, 2], scope='pool3')

        conv4_1 = slim.conv2d(pool3, 512, [3, 3], scope='conv4_1')
        conv4_2 = slim.conv2d(conv4_1, 512, [3, 3], scope='conv4_2')
        conv4_3 = slim.conv2d(conv4_2, 512, [3, 3], scope='conv4_3')
        pool4 = slim.max_pool2d(conv4_3, [2, 2], scope='pool4')

        conv5_1 = slim.conv2d(pool4, 512, [3, 3], scope='conv5_1')
        conv5_2 = slim.conv2d(conv5_1, 512, [3, 3], scope='conv5_2')
        conv5_3 = slim.conv2d(conv5_2, 512, [3, 3], scope='conv5_3')
        pool5 = slim.max_pool2d(conv5_3, [2, 2], scope='pool5')

        flatten5 = slim.flatten(pool5, scope='flatten5')
        fc6 = slim.fully_connected(flatten5, 4096, scope='fc6')
        dropout6 = slim.dropout(fc6, 0.9, scope='dropout6')
        fc7 = slim.fully_connected(dropout6, 4096, scope='fc7')
        dropout7 = slim.dropout(fc7, 0.9, scope='dropout7')
        fc8 = slim.fully_connected(dropout7, 101, activation_fn=None, scope='fc8')
        prob = tf.nn.softmax(fc8)
        predictions = tf.argmax(prob, 1)

        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(fc8, labels)
        actionLoss = tf.reduce_mean(cross_entropy)

        zeroCon = tf.constant(0)
        losses = [zeroCon, zeroCon, zeroCon, zeroCon, zeroCon, zeroCon, actionLoss]
        flows_all = [zeroCon, zeroCon, zeroCon, zeroCon, zeroCon, zeroCon, prob]

        slim.losses.add_loss(actionLoss)
        
        return losses, flows_all, predictions

def STsingle(inputs, outputs, loss_weight, labels):
    # Mean subtraction (BGR) for flying chairs
    mean = tf.constant([104.0, 117.0, 123.0], dtype=tf.float32, name="img_global_mean")
    # tf.tile(mean, [4,192,256,1])
    inputs = inputs - mean
    outputs = outputs - mean
    # Scaling to 0 ~ 1 or -0.4 ~ 0.6?
    inputs = tf.truediv(inputs, 255.0)
    outputs = tf.truediv(outputs, 255.0)

    # Add local response normalization (ACROSS_CHANNELS) for computing photometric loss
    inputs_norm = tf.nn.local_response_normalization(inputs, depth_radius=4, beta=0.7)
    outputs_norm = tf.nn.local_response_normalization(outputs, depth_radius=4, beta=0.7)

    with slim.arg_scope([slim.conv2d, slim.conv2d_transpose, slim.fully_connected], 
                        activation_fn=tf.nn.elu):

        '''
        Shared conv layers
        '''
        conv1_1 = slim.conv2d(tf.concat(3, [inputs, outputs]), 64, [3, 3], scope='conv1_1')
        # conv1_1 = slim.conv2d(inputs, 64, [3, 3], scope='conv1_1')
        conv1_2 = slim.conv2d(conv1_1, 64, [3, 3], scope='conv1_2')
        pool1 = slim.max_pool2d(conv1_2, [2, 2], scope='pool1')

        conv2_1 = slim.conv2d(pool1, 128, [3, 3], scope='conv2_1')
        conv2_2 = slim.conv2d(conv2_1, 128, [3, 3], scope='conv2_2')
        pool2 = slim.max_pool2d(conv2_2, [2, 2], scope='pool2')

        conv3_1 = slim.conv2d(pool2, 256, [3, 3], scope='conv3_1')
        conv3_2 = slim.conv2d(conv3_1, 256, [3, 3], scope='conv3_2')
        conv3_3 = slim.conv2d(conv3_2, 256, [3, 3], scope='conv3_3')
        pool3 = slim.max_pool2d(conv3_3, [2, 2], scope='pool3')

        conv4_1 = slim.conv2d(pool3, 512, [3, 3], scope='conv4_1')
        conv4_2 = slim.conv2d(conv4_1, 512, [3, 3], scope='conv4_2')
        conv4_3 = slim.conv2d(conv4_2, 512, [3, 3], scope='conv4_3')
        pool4 = slim.max_pool2d(conv4_3, [2, 2], scope='pool4')

        conv5_1 = slim.conv2d(pool4, 512, [3, 3], scope='conv5_1')
        conv5_2 = slim.conv2d(conv5_1, 512, [3, 3], scope='conv5_2')
        conv5_3 = slim.conv2d(conv5_2, 512, [3, 3], scope='conv5_3')
        pool5 = slim.max_pool2d(conv5_3, [2, 2], scope='pool5')
        # print pool5.get_shape()
        '''
        Spatial branch
        '''
        flatten5 = slim.flatten(pool5, scope='flatten5')
        fc6 = slim.fully_connected(flatten5, 4096, scope='fc6')
        dropout6 = slim.dropout(fc6, 0.9, scope='dropout6')
        fc7 = slim.fully_connected(dropout6, 4096, scope='fc7')
        dropout7 = slim.dropout(fc7, 0.9, scope='dropout7')
        fc8 = slim.fully_connected(dropout7, 101, activation_fn=None, scope='fc8')
        prob = tf.nn.softmax(fc8)
        actionPredictions = tf.argmax(prob, 1)

        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(fc8, labels)
        actionLoss = tf.reduce_mean(cross_entropy)

        '''
        Temporal branch
        '''
        # Hyper-params for computing unsupervised loss
        epsilon = 0.0001 
        alpha_c = 0.3
        alpha_s = 0.3
        lambda_smooth = 0.8
        FlowDeltaWeights = tf.constant([0,0,0,0,1,-1,0,0,0,0,0,0,0,1,0,0,-1,0], dtype=tf.float32, shape=[3,3,2,2], name="FlowDeltaWeights")
        scale = 2       # for deconvolution

        # Expanding part
        pr5 = slim.conv2d(pool5, 2, [3, 3], activation_fn=None, scope='pr5')
        h5 = pr5.get_shape()[1].value
        w5 = pr5.get_shape()[2].value
        pr5_input = tf.image.resize_bilinear(inputs_norm, [h5, w5])
        pr5_output = tf.image.resize_bilinear(outputs_norm, [h5, w5])
        flow_scale_5 = 0.625    # (*20/32)
        loss5, _ = loss_interp(pr5, pr5_input, pr5_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_5, FlowDeltaWeights)
        upconv4 = slim.conv2d_transpose(pool5, 256, [2*scale, 2*scale], stride=scale, scope='upconv4')
        pr5to4 = slim.conv2d_transpose(pr5, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr5to4')
        concat4 = tf.concat(3, [pool4, upconv4, pr5to4])

        pr4 = slim.conv2d(concat4, 2, [3, 3], activation_fn=None, scope='pr4')
        h4 = pr4.get_shape()[1].value
        w4 = pr4.get_shape()[2].value
        pr4_input = tf.image.resize_bilinear(inputs_norm, [h4, w4])
        pr4_output = tf.image.resize_bilinear(outputs_norm, [h4, w4])
        flow_scale_4 = 1.25    # (*20/16)
        loss4, _ = loss_interp(pr4, pr4_input, pr4_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_4, FlowDeltaWeights)
        upconv3 = slim.conv2d_transpose(concat4, 128, [2*scale, 2*scale], stride=scale, scope='upconv3')
        pr4to3 = slim.conv2d_transpose(pr4, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr4to3')
        concat3 = tf.concat(3, [pool3, upconv3, pr4to3])

        pr3 = slim.conv2d(concat3, 2, [3, 3], activation_fn=None, scope='pr3')
        h3 = pr3.get_shape()[1].value
        w3 = pr3.get_shape()[2].value
        pr3_input = tf.image.resize_bilinear(inputs_norm, [h3, w3])
        pr3_output = tf.image.resize_bilinear(outputs_norm, [h3, w3])
        flow_scale_3 = 2.5    # (*20/8)
        loss3, _ = loss_interp(pr3, pr3_input, pr3_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_3, FlowDeltaWeights)
        upconv2 = slim.conv2d_transpose(concat3, 64, [2*scale, 2*scale], stride=scale, scope='upconv2')
        pr3to2 = slim.conv2d_transpose(pr3, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr3to2')
        concat2 = tf.concat(3, [pool2, upconv2, pr3to2])

        pr2 = slim.conv2d(concat2, 2, [3, 3], activation_fn=None, scope='pr2')
        h2 = pr2.get_shape()[1].value
        w2 = pr2.get_shape()[2].value
        pr2_input = tf.image.resize_bilinear(inputs_norm, [h2, w2])
        pr2_output = tf.image.resize_bilinear(outputs_norm, [h2, w2])
        flow_scale_2 = 5.0    # (*20/4)
        loss2, _ = loss_interp(pr2, pr2_input, pr2_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_2, FlowDeltaWeights)
        upconv1 = slim.conv2d_transpose(concat2, 32, [2*scale, 2*scale], stride=scale, scope='upconv1')
        pr2to1 = slim.conv2d_transpose(pr2, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr2to1')
        concat1 = tf.concat(3, [pool1, upconv1, pr2to1])

        pr1 = slim.conv2d(concat1, 2, [3, 3], activation_fn=None, scope='pr1')
        h1 = pr1.get_shape()[1].value
        w1 = pr1.get_shape()[2].value
        pr1_input = tf.image.resize_bilinear(inputs_norm, [h1, w1])
        pr1_output = tf.image.resize_bilinear(outputs_norm, [h1, w1])
        flow_scale_1 = 10.0    # (*20/2) 
        loss1, prev1 = loss_interp(pr1, pr1_input, pr1_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_1, FlowDeltaWeights)
        
        # Adding intermediate losses
        all_loss = loss_weight[0]*loss1["total"] + loss_weight[1]*loss2["total"] + loss_weight[2]*loss3["total"] + \
                    loss_weight[3]*loss4["total"] + loss_weight[4]*loss5["total"] + loss_weight[0]*actionLoss
        slim.losses.add_loss(all_loss)

        losses = [loss1, loss2, loss3, loss4, loss5, actionLoss]
        flows_all = [pr1*flow_scale_1, pr2*flow_scale_2, pr3*flow_scale_3, pr4*flow_scale_4, pr5*flow_scale_5]
        
        predictions = [prev1, actionPredictions]
        return losses, flows_all, predictions


def STbaseline(inputs, outputs, loss_weight, labels):
    """
    Spatial stream based on VGG16
    Temporal stream based on Flownet simple
    """

    # Mean subtraction (BGR) for flying chairs
    mean = tf.constant([104.0, 117.0, 123.0], dtype=tf.float32, name="img_global_mean")
    # tf.tile(mean, [4,192,256,1])
    inputs = inputs - mean
    outputs = outputs - mean
    # Scaling to 0 ~ 1 or -0.4 ~ 0.6?
    inputs = tf.truediv(inputs, 255.0)
    outputs = tf.truediv(outputs, 255.0)

    # Add local response normalization (ACROSS_CHANNELS) for computing photometric loss
    inputs_norm = tf.nn.local_response_normalization(inputs, depth_radius=4, beta=0.7)
    outputs_norm = tf.nn.local_response_normalization(outputs, depth_radius=4, beta=0.7)

    with slim.arg_scope([slim.conv2d, slim.conv2d_transpose], 
                        activation_fn=tf.nn.elu):       # original use leaky ReLU, now we use elu
        # Contracting part
        Tconv1   = slim.conv2d(tf.concat(3, [inputs, outputs]), 64, [7, 7], stride=2, scope='Tconv1')
        Tconv2   = slim.conv2d(Tconv1, 128, [5, 5], stride=2, scope='Tconv2')
        Tconv3_1 = slim.conv2d(Tconv2, 256, [5, 5], stride=2, scope='Tconv3_1')
        Tconv3_2 = slim.conv2d(Tconv3_1, 256, [3, 3], scope='Tconv3_2')
        Tconv4_1 = slim.conv2d(Tconv3_2, 512, [3, 3], stride=2, scope='Tconv4_1')
        Tconv4_2 = slim.conv2d(Tconv4_1, 512, [3, 3], scope='Tconv4_2')
        Tconv5_1 = slim.conv2d(Tconv4_2, 512, [3, 3], stride=2, scope='Tconv5_1')
        Tconv5_2 = slim.conv2d(Tconv5_1, 512, [3, 3], scope='Tconv5_2')
        Tconv6_1 = slim.conv2d(Tconv5_2, 1024, [3, 3], stride=2, scope='Tconv6_1')
        Tconv6_2 = slim.conv2d(Tconv6_1, 1024, [3, 3], scope='Tconv6_2')

        # Hyper-params for computing unsupervised loss
        epsilon = 0.0001 
        alpha_c = 0.25
        alpha_s = 0.37
        lambda_smooth = 1.0
        FlowDeltaWeights = tf.constant([0,0,0,0,1,-1,0,0,0,0,0,0,0,1,0,0,-1,0], dtype=tf.float32, shape=[3,3,2,2], name="FlowDeltaWeights")
        scale = 2       # for deconvolution

        # Expanding part
        pr6 = slim.conv2d(Tconv6_2, 2, [3, 3], activation_fn=None, scope='pr6')
        h6 = pr6.get_shape()[1].value
        w6 = pr6.get_shape()[2].value
        pr6_input = tf.image.resize_bilinear(inputs_norm, [h6, w6])
        pr6_output = tf.image.resize_bilinear(outputs_norm, [h6, w6])
        flow_scale_6 = 0.3125    # (*20/64)
        loss6, _ = loss_interp(pr6, pr6_input, pr6_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_6, FlowDeltaWeights)
        upconv5 = slim.conv2d_transpose(Tconv6_2, 512, [2*scale, 2*scale], stride=scale, scope='upconv5')
        pr6to5 = slim.conv2d_transpose(pr6, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr6to5')
        concat5 = tf.concat(3, [Tconv5_2, upconv5, pr6to5])

        pr5 = slim.conv2d(concat5, 2, [3, 3], activation_fn=None, scope='pr5')
        h5 = pr5.get_shape()[1].value
        w5 = pr5.get_shape()[2].value
        pr5_input = tf.image.resize_bilinear(inputs_norm, [h5, w5])
        pr5_output = tf.image.resize_bilinear(outputs_norm, [h5, w5])
        flow_scale_5 = 0.625    # (*20/32)
        loss5, _ = loss_interp(pr5, pr5_input, pr5_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_5, FlowDeltaWeights)
        upconv4 = slim.conv2d_transpose(concat5, 256, [2*scale, 2*scale], stride=scale, scope='upconv4')
        pr5to4 = slim.conv2d_transpose(pr5, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr5to4')
        concat4 = tf.concat(3, [Tconv4_2, upconv4, pr5to4])

        pr4 = slim.conv2d(concat4, 2, [3, 3], activation_fn=None, scope='pr4')
        h4 = pr4.get_shape()[1].value
        w4 = pr4.get_shape()[2].value
        pr4_input = tf.image.resize_bilinear(inputs_norm, [h4, w4])
        pr4_output = tf.image.resize_bilinear(outputs_norm, [h4, w4])
        flow_scale_4 = 1.25    # (*20/16)
        loss4, _ = loss_interp(pr4, pr4_input, pr4_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_4, FlowDeltaWeights)
        upconv3 = slim.conv2d_transpose(concat4, 128, [2*scale, 2*scale], stride=scale, scope='upconv3')
        pr4to3 = slim.conv2d_transpose(pr4, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr4to3')
        concat3 = tf.concat(3, [Tconv3_2, upconv3, pr4to3])

        pr3 = slim.conv2d(concat3, 2, [3, 3], activation_fn=None, scope='pr3')
        h3 = pr3.get_shape()[1].value
        w3 = pr3.get_shape()[2].value
        pr3_input = tf.image.resize_bilinear(inputs_norm, [h3, w3])
        pr3_output = tf.image.resize_bilinear(outputs_norm, [h3, w3])
        flow_scale_3 = 2.5    # (*20/8)
        loss3, _ = loss_interp(pr3, pr3_input, pr3_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_3, FlowDeltaWeights)
        upconv2 = slim.conv2d_transpose(concat3, 64, [2*scale, 2*scale], stride=scale, scope='upconv2')
        pr3to2 = slim.conv2d_transpose(pr3, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr3to2')
        concat2 = tf.concat(3, [Tconv2, upconv2, pr3to2])

        pr2 = slim.conv2d(concat2, 2, [3, 3], activation_fn=None, scope='pr2')
        h2 = pr2.get_shape()[1].value
        w2 = pr2.get_shape()[2].value
        pr2_input = tf.image.resize_bilinear(inputs_norm, [h2, w2])
        pr2_output = tf.image.resize_bilinear(outputs_norm, [h2, w2])
        flow_scale_2 = 5.0    # (*20/4)
        loss2, _ = loss_interp(pr2, pr2_input, pr2_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_2, FlowDeltaWeights)
        upconv1 = slim.conv2d_transpose(concat2, 32, [2*scale, 2*scale], stride=scale, scope='upconv1')
        pr2to1 = slim.conv2d_transpose(pr2, 2, [2*scale, 2*scale], stride=scale, activation_fn=None, scope='up_pr2to1')
        concat1 = tf.concat(3, [Tconv1, upconv1, pr2to1])

        pr1 = slim.conv2d(concat1, 2, [3, 3], activation_fn=None, scope='pr1')
        h1 = pr1.get_shape()[1].value
        w1 = pr1.get_shape()[2].value
        pr1_input = tf.image.resize_bilinear(inputs_norm, [h1, w1])
        pr1_output = tf.image.resize_bilinear(outputs_norm, [h1, w1])
        flow_scale_1 = 10.0    # (*20/2) 
        loss1, prev1 = loss_interp(pr1, pr1_input, pr1_output, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale_1, FlowDeltaWeights)
        
    with slim.arg_scope([slim.conv2d, slim.fully_connected], 
                        activation_fn=tf.nn.relu,
                        weights_initializer=tf.truncated_normal_initializer(0.0, 0.01),
                        weights_regularizer=slim.l2_regularizer(0.0005)):

        # conv1_1 = slim.conv2d(tf.concat(3, [inputs, outputs]), 64, [3, 3], scope='conv1_1')
        conv1_1 = slim.conv2d(inputs, 64, [3, 3], scope='conv1_1')
        conv1_2 = slim.conv2d(conv1_1, 64, [3, 3], scope='conv1_2')
        pool1 = slim.max_pool2d(conv1_2, [2, 2], scope='pool1')

        conv2_1 = slim.conv2d(pool1, 128, [3, 3], scope='conv2_1')
        conv2_2 = slim.conv2d(conv2_1, 128, [3, 3], scope='conv2_2')
        pool2 = slim.max_pool2d(conv2_2, [2, 2], scope='pool2')

        conv3_1 = slim.conv2d(pool2, 256, [3, 3], scope='conv3_1')
        conv3_2 = slim.conv2d(conv3_1, 256, [3, 3], scope='conv3_2')
        conv3_3 = slim.conv2d(conv3_2, 256, [3, 3], scope='conv3_3')
        pool3 = slim.max_pool2d(conv3_3, [2, 2], scope='pool3')

        conv4_1 = slim.conv2d(pool3, 512, [3, 3], scope='conv4_1')
        conv4_2 = slim.conv2d(conv4_1, 512, [3, 3], scope='conv4_2')
        conv4_3 = slim.conv2d(conv4_2, 512, [3, 3], scope='conv4_3')
        pool4 = slim.max_pool2d(conv4_3, [2, 2], scope='pool4')

        conv5_1 = slim.conv2d(pool4, 512, [3, 3], scope='conv5_1')
        conv5_2 = slim.conv2d(conv5_1, 512, [3, 3], scope='conv5_2')
        conv5_3 = slim.conv2d(conv5_2, 512, [3, 3], scope='conv5_3')
        pool5 = slim.max_pool2d(conv5_3, [2, 2], scope='pool5')

        # Incorporate temporal feature
        concatST = tf.concat(3, [pool5, Tconv5_2])
        poolST = slim.max_pool2d(concatST, [2, 2])
        # print poolST.get_shape()
        concat2ST = tf.concat(3, [poolST, Tconv6_2])
        # print concat2ST.get_shape()
        concatDR = slim.conv2d(concat2ST, 512, [1, 1])
        # print concatDR.get_shape()

        flatten5 = slim.flatten(concatDR, scope='flatten5')
        fc6 = slim.fully_connected(flatten5, 4096, scope='fc6')
        dropout6 = slim.dropout(fc6, 0.9, scope='dropout6')
        fc7 = slim.fully_connected(dropout6, 4096, scope='fc7')
        dropout7 = slim.dropout(fc7, 0.9, scope='dropout7')
        fc8 = slim.fully_connected(dropout7, 101, activation_fn=None, scope='fc8')
        prob = tf.nn.softmax(fc8)
        actionPredictions = tf.argmax(prob, 1)

        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(fc8, labels)
        actionLoss = tf.reduce_mean(cross_entropy)

        # Adding intermediate losses
        all_loss = loss_weight[0]*loss1["total"] + loss_weight[1]*loss2["total"] + loss_weight[2]*loss3["total"] + \
                    loss_weight[3]*loss4["total"] + loss_weight[4]*loss5["total"] + loss_weight[5]*loss6["total"] + \
                    loss_weight[0]*actionLoss
        slim.losses.add_loss(all_loss)

        losses = [loss1, loss2, loss3, loss4, loss5, loss6, actionLoss]
        # pr1 = tf.mul(tf.constant(20.0), pr1)
        flows_all = [pr1*flow_scale_1, pr2*flow_scale_2, pr3*flow_scale_3, pr4*flow_scale_4, pr5*flow_scale_5, pr6*flow_scale_6]
        
        predictions = [prev1, actionPredictions]
        return losses, flows_all, predictions


def loss_interp(flows, inputs, outputs, epsilon, alpha_c, alpha_s, lambda_smooth, flow_scale, FlowDeltaWeights):

    shape = inputs.get_shape()
    shape = [int(dim) for dim in shape]
    num_batch = shape[0]
    height = shape[1]
    width = shape[2]
    channels = shape[3]

    needMask = True
    # Create border mask for image
    border_ratio = 0.1
    shortestDim = height
    borderWidth = int(np.ceil(shortestDim * border_ratio))
    smallerMask = tf.ones([height-2*borderWidth, width-2*borderWidth])
    borderMask = tf.pad(smallerMask, [[borderWidth,borderWidth], [borderWidth,borderWidth]], "CONSTANT")
    borderMask = tf.tile(tf.expand_dims(borderMask, 0), [num_batch, 1, 1])
    borderMaskImg = tf.tile(tf.expand_dims(borderMask, 3), [1, 1, 1, channels])
    borderMaskFlow = tf.tile(tf.expand_dims(borderMask, 3), [1, 1, 1, 2])

    # Create smoothness border mask for optical flow
    smallerSmoothMaskU = tf.ones([height, width-1])
    smallerSmoothMaskV = tf.ones([height-1, width])
    smoothnessMaskU = tf.pad(smallerSmoothMaskU, [[0,0], [0,1]], "CONSTANT")
    smoothnessMaskV = tf.pad(smallerSmoothMaskV, [[0,1], [0,0]], "CONSTANT")
    smoothnessMask = tf.pack([smoothnessMaskU, smoothnessMaskV], axis=2)
    smoothnessMask = tf.tile(tf.expand_dims(smoothnessMask, 0), [num_batch, 1, 1, 1])

    inputs_flat = tf.reshape(inputs, [num_batch, -1, channels])
    outputs_flat = tf.reshape(outputs, [num_batch, -1, channels])
    borderMask_flat = tf.reshape(borderMaskImg, [num_batch, -1, channels])

    flows = tf.mul(flows, flow_scale)
    flows_flat = tf.reshape(flows, [num_batch, -1, 2])
    floor_flows = tf.to_int32(tf.floor(flows_flat))
    weights_flows = flows_flat - tf.floor(flows_flat)

    # Construct the grids
    pos_x = tf.range(height)
    pos_x = tf.tile(tf.expand_dims(pos_x, 1), [1, width])
    pos_x = tf.reshape(pos_x, [-1])
    pos_y = tf.range(width)
    pos_y = tf.tile(tf.expand_dims(pos_y, 0), [height, 1])
    pos_y = tf.reshape(pos_y, [-1])
    zero = tf.zeros([], dtype='int32')

    # Warp two images based on optical flow
    batch = []
    for b in range(num_batch):
        channel = []
        x = floor_flows[b, :, 0]
        y = floor_flows[b, :, 1]
        xw = weights_flows[b, :, 0]
        yw = weights_flows[b, :, 1]

        for c in range(channels):

            x0 = pos_y + x
            x1 = x0 + 1
            y0 = pos_x + y
            y1 = y0 + 1

            x0 = tf.clip_by_value(x0, zero, width-1)
            x1 = tf.clip_by_value(x1, zero, width-1)
            y0 = tf.clip_by_value(y0, zero, height-1)
            y1 = tf.clip_by_value(y1, zero, height-1)

            idx_a = y0 * width + x0
            idx_b = y1 * width + x0
            idx_c = y0 * width + x1
            idx_d = y1 * width + x1

            Ia = tf.gather(outputs_flat[b, :, c], idx_a)
            Ib = tf.gather(outputs_flat[b, :, c], idx_b)
            Ic = tf.gather(outputs_flat[b, :, c], idx_c)
            Id = tf.gather(outputs_flat[b, :, c], idx_d)

            wa = (1-xw) * (1-yw)
            wb = (1-xw) * yw
            wc = xw * (1-yw)
            wd = xw * yw

            img = tf.mul(Ia, wa) + tf.mul(Ib, wb) + tf.mul(Ic, wc) + tf.mul(Id, wd)
            channel.append(img)
        batch.append(tf.pack(channel, axis=1))
    reconstructs = tf.pack(batch)
    
    # Recostruction loss
    diff_reconstruct = tf.scalar_mul(255.0, tf.sub(reconstructs, inputs_flat))
    eleWiseLoss = tf.pow(tf.square(diff_reconstruct) + tf.square(epsilon), alpha_c)
    Charbonnier_reconstruct = 0.0
    numValidPixels = 0.0
    if needMask:
        eleWiseLoss = tf.mul(borderMask_flat, eleWiseLoss)
        validPixels = tf.equal(borderMask_flat, tf.ones_like(borderMask_flat))
        numValidPixels = tf.to_float(tf.reduce_sum(tf.to_int32(validPixels)))
        Charbonnier_reconstruct = tf.reduce_sum(eleWiseLoss) / numValidPixels
    else:
        Charbonnier_reconstruct = tf.reduce_mean(eleWiseLoss)

    # Smoothness loss
    flow_delta = tf.nn.conv2d(flows, FlowDeltaWeights, [1,1,1,1], padding="SAME")
    U_loss = 0.0
    V_loss = 0.0
    if needMask:
        flow_delta_clean = tf.mul(flow_delta, smoothnessMask)   # why need smoothness mask
        flow_delta_clean = tf.mul(flow_delta_clean, borderMaskFlow)     
        U_eleWiseLoss = tf.pow(tf.square(flow_delta_clean[:,:,:,0]) + tf.square(epsilon), alpha_s)
        U_loss = tf.reduce_sum(U_eleWiseLoss) / numValidPixels
        V_eleWiseLoss = tf.pow(tf.square(flow_delta_clean[:,:,:,1]) + tf.square(epsilon), alpha_s)
        V_loss = tf.reduce_sum(V_eleWiseLoss) / numValidPixels
    else:
        U_loss = tf.reduce_mean(tf.pow(tf.square(flow_delta[:,:,:,0] * flow_scale)  + tf.square(epsilon), alpha_s)) 
        V_loss = tf.reduce_mean(tf.pow(tf.square(flow_delta[:,:,:,1] * flow_scale)  + tf.square(epsilon), alpha_s))
    loss_smooth = U_loss + V_loss

    total_loss = Charbonnier_reconstruct + lambda_smooth * loss_smooth
    # Define a loss structure
    lossDict = {}
    lossDict["total"] = total_loss
    lossDict["Charbonnier_reconstruct"] = Charbonnier_reconstruct
    lossDict["U_loss"] = U_loss
    lossDict["V_loss"] = V_loss

    return lossDict, tf.reshape(reconstructs, [num_batch, height, width, 3])
