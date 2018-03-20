from builtins import range
from builtins import object
import numpy as np
from numpy import linalg as LA

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - dropout: Scalar between 0 and 1 giving dropout strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        #print("input hidden out",input_dim, hidden_dim, num_classes)
        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian with standard deviation equal to   #
        # weight_scale, and biases should be initialized to zero. All weights and  #
        # biases should be stored in the dictionary self.params, with first layer  #
        # weights and biases using the keys 'W1' and 'b1' and second layer weights #
        # and biases using the keys 'W2' and 'b2'.                                 #
        ############################################################################
        flat_random = np.random.normal(0,weight_scale,input_dim * hidden_dim)
        self.params['W1'] = flat_random.reshape(input_dim, hidden_dim)
        self.params['b1'] = np.zeros(hidden_dim)
        
        flat_random = np.random.normal(0,weight_scale,hidden_dim * num_classes)
        self.params['W2'] = flat_random.reshape(hidden_dim, num_classes)
        self.params['b2'] = np.zeros(num_classes)
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        N = X.shape[0]
        C = self.num_classes
        #print("x shape",X.shape)
        out,self.first_cache = affine_relu_forward(X, self.params['W1'], self.params['b1'])
        scores,self.second_cache = affine_forward(out, self.params['W2'], self.params['b2'])
        #print("scores.shape",scores.shape)
        #print("N C",N,C)
#         for i in range(N):
#             for j in range(C):
#                 scores[i][j] = soft_max(scores[i][j])
        #
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dx = softmax_loss(scores, y)
        loss += 0.5 * self.reg * LA.norm(self.params['W2'])**2
        loss += 0.5 * self.reg * LA.norm(self.params['W1'])**2
        
        #loss += 0.5 * self.reg * LA.norm(self.params['b2'])
        #loss += 0.5 * self.reg * LA.norm(self.params['b1'])
        
        dx, dw, db = affine_backward(dx, self.second_cache)
        dw += self.reg * self.params['W2']
        grads['W2'], grads['b2'] = dw,db
        
        dx, dw, db = affine_relu_backward(dx, self.first_cache)
        dw += self.reg * self.params['W1']
        grads['W1'], grads['b1'] = dw,db
#         grads['W1'] -= 0.5*self.reg*grads['W1']
#         grads['W2'] -= 0.5*self.reg*grads['W2']
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads






class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=0, use_batchnorm=False, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=0 then
          the network should not use dropout at all.
        - use_batchnorm: Whether or not the network should use batch normalization.
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.use_batchnorm = use_batchnorm
        self.use_dropout = dropout > 0
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution with standard deviation equal to  #
        # weight_scale and biases should be initialized to zero.                   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to one and shift      #
        # parameters should be initialized to zero.                                #
        ############################################################################
        print("Hidden_dims", hidden_dims)
        self.num_classes = num_classes
        self.params['W1'] = np.random.normal(scale = weight_scale,size = (input_dim, hidden_dims[0]))
        self.params['b1'] = np.zeros(hidden_dims[0])

        layer_count = 2
        
        while(layer_count <= len(hidden_dims)):
            self.params['W' + str(layer_count)] = np.random.normal(scale = weight_scale,size = (hidden_dims[layer_count - 2], hidden_dims[layer_count - 1] ))
            self.params['b' + str(layer_count)] = np.zeros(hidden_dims[layer_count - 1])
            layer_count += 1
        
        #for the final layer
        self.params['W' + str(layer_count)] = np.random.normal(scale = weight_scale,size = (hidden_dims[-1], num_classes))
        self.params['b' + str(layer_count)] = np.zeros(num_classes)
        
        #set gammas and betas if batchnorm, except the last layer
        if use_batchnorm:
        	for t in range(self.num_layers - 1):
        		self.params['gamma' + str(t + 1)] = np.ones(hidden_dims[t])	
        		self.params['beta' + str(t + 1)] = np.zeros(hidden_dims[t])

        if self.use_dropout:
            print('Init Dropout')
        print("init complete")
        print("layer c",layer_count)
        
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.use_batchnorm:
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.use_batchnorm:
            for bn_param in self.bn_params:
                bn_param['mode'] = mode

        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        N = X.shape[0]
        C = self.num_classes
        out = [0]*(self.num_layers + 1)
        self.ar_f_cache = [0]*(self.num_layers + 1)
        self.drop_cache = [0]*(self.num_layers + 1)
        
        #print("x shape",X.shape)
        out[0] = X
        for t in range(1, self.num_layers):
            #print("In loop",'W' + str(t))
            if self.use_batchnorm:
            	out[t],self.ar_f_cache[t] = affine_batch_relu_forward(out[t - 1],
            	self.params['W' + str(t)], self.params['b' + str(t)],self.params['gamma' + str(t)],
            	self.params['beta'+str(t)],self.bn_params[t - 1])
            else:
            	out[t],self.ar_f_cache[t] = affine_relu_forward(out[t - 1], self.params['W' + str(t)], self.params['b' + str(t)])
        	
            if self.use_dropout:
                out[t],self.drop_cache[t] = dropout_forward(out[t], self.dropout_param)

        out[self.num_layers],self.ar_f_cache[self.num_layers] = \
        affine_forward(out[self.num_layers - 1], self.params['W' + str(self.num_layers)], self.params['b' + str(self.num_layers)])
        
        scores = out[self.num_layers]
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores
            
        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dx = softmax_loss(scores, y)
        for i in range(1, self.num_layers + 1):
            loss += 0.5 * self.reg * LA.norm(self.params['W' + str(i)])**2
             
        layer_count = self.num_layers
        dx, dw, db = affine_backward(dx, self.ar_f_cache[layer_count])
        dw += self.reg * self.params['W' + str(layer_count)]
        grads['W' + str(layer_count)], grads['b' + str(layer_count)] = dw,db
        
        while(layer_count > 1):
            layer_count -= 1
            if self.use_dropout:
                dx = dropout_backward(dx, self.drop_cache[layer_count])
                
            if self.use_batchnorm:
            	dx, dw, db, dgamma, dbeta = affine_batch_relu_backward(dx, self.ar_f_cache[layer_count])
            else:
            	dx, dw, db = affine_relu_backward(dx, self.ar_f_cache[layer_count])
            dw += self.reg * self.params['W' + str(layer_count)]
            grads['W' + str(layer_count)], grads['b' + str(layer_count)] = dw,db
            if self.use_batchnorm:
        	    grads['gamma' + str(layer_count)] = dgamma
        	    grads['beta' + str(layer_count)] = dbeta
            	
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
    
def affine_batch_relu_forward(x, w, b, gamma, beta, bn_params):
    """
    Convenience layer that performs an affine transform followed 
    by a batch and then a ReLU

    Inputs:
    - x: Input to the affine layer
    - w, b: Weights for the affine layer

    Returns a tuple of:
    - out: Output from the ReLU
    - cache: Object to give to the backward pass
    """
    a, fc_cache = affine_forward(x, w, b)
    #print("a shape", a.shape)
    #print("gshape", gamma.shape)
    #print('bshape',beta.shape)
    a_norm, batch_cache = batchnorm_forward(a, gamma, beta, bn_params)
    out, relu_cache = relu_forward(a_norm)
    cache = (fc_cache, batch_cache, relu_cache)
    return out, cache

def affine_batch_relu_backward(dout, cache):
    """
    Backward pass for the affine-batch-relu
    """
    fc_cache, batch_cache, relu_cache = cache
    da = relu_backward(dout, relu_cache)
    dx,dgamma,dbeta = batchnorm_backward(da,batch_cache)
    dx, dw, db = affine_backward(dx, fc_cache)
    return dx, dw, db, dgamma, dbeta