from unittest import TestCase
from ebisu import *
from ebisu.alternate import *

import unittest

def relerr(dirt, gold):
  return abs(dirt - gold) / abs(gold)

def maxrelerr(dirts, golds):
  return max(map(relerr, dirts, golds))

def klDivBeta(a, b, a2, b2):
  """Kullback-Leibler divergence between two Beta distributions in nats"""
  # Via http://bariskurt.com/kullback-leibler-divergence-between-two-dirichlet-and-beta-distributions/
  from scipy.special import gammaln, psi
  import numpy as np
  left = np.array([a, b])
  right = np.array([a2, b2])
  return gammaln(sum(left)) - gammaln(sum(right)) - sum(gammaln(left)) + sum(gammaln(right)) + np.dot(left - right, psi(left) - psi(sum(left)))


class TestEbisu(unittest.TestCase):
  def test_kl(self):
    # See https://en.wikipedia.org/w/index.php?title=Beta_distribution&oldid=774237683#Quantities_of_information_.28entropy.29 for these numbers
    self.assertAlmostEqual(klDivBeta(1., 1., 3., 3.), 0.598803, places=5)
    self.assertAlmostEqual(klDivBeta(3., 3., 1., 1.), 0.267864, places=5)

  def test_prior(self):
    def inner(a, b, t0):
      for t in map(lambda dt: dt * t0, [0.1, .99, 1., 1.01, 5.5]):
        mc = recallProbabilityMonteCarlo(a, b, t0, t, N=100*1000)
        mean = recallProbabilityMean(a, b, t0, t)
        var = recallProbabilityVar(a, b, t0, t)
        self.assertLess(relerr(mean, mc['mean']), 3e-2)

    inner(3.3, 4.4, 5.5)
    inner(3.3, 4.4, 15.5)
    inner(3.3, 4.4, .5)
    inner(34.4, 34.4, 5.5)
    inner(34.4, 34.4, 15.5)
    inner(34.4, 34.4, .5)

  def test_posterior(self):
    def inner(a, b, t0):
      kl = lambda v, w: (klDivBeta(v[0], v[1], w[0], w[1]) + klDivBeta(w[0], w[1], v[0], v[1])) / 2.
      for t in map(lambda dt: dt * t0, [0.1, 1., 5.5]):
        for x in [0., 1.]:
          msg = 'a={},b={},t0={},x={},t={}'.format(a, b, t0, x, t)
          mc = posteriorMonteCarlo(a, b, t0, x, t, N=1*1000*1000)
          an = posteriorAnalytic(a, b, t0, x, t)
          self.assertLess(kl(an, mc), 1e-4, msg=msg)

          try:
            quad1 = posteriorQuad(a, b, t0, x, t, analyticMarginal=True)
          except OverflowError:
            quad1 = None
          if quad1 is not None:
            self.assertLess(kl(quad1, mc), 1e-4, msg=msg)

          try:
            quad2 = posteriorQuad(a, b, t0, x, t, analyticMarginal=False)
          except OverflowError:
            quad2 = None
          if quad2 is not None:
            self.assertLess(kl(quad2, mc), 1e-4, msg=msg)

    inner(3.3, 4.4, 5.5)
    inner(3.3, 4.4, 15.5)
    inner(3.3, 4.4, .5)
    inner(34.4, 34.4, 5.5)
    inner(34.4, 34.4, 15.5)
    inner(34.4, 34.4, .5)

if __name__ == '__main__':
  unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule(TestEbisu()))
