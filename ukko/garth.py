# -*- coding: utf-8 -*-

from activity_list import ActivityList
from sgs import SSGS
from schedule import Schedule
from rthypothesis import RTSystem

import numpy as np
import random


class GARTH(object):
    def __init__(self, problem, **kwargs):
        self.problem = problem
        self.params = {'popSize': 100,
                       'Rcopy': 0.1,
                       'Rnew': 0.0,
                       'Rmut': 0.2,
                       'Rcross': 0.7,
                       'nSelJobs': 5,
                       'dist': 10000,
                       'schedule_limit': 5000}
        self.params.update(kwargs)
        for key in ('Rcopy', 'Rnew', 'Rmut', 'Rcross'):
            self.params['num' + key] = int(self.params['popSize'] * self.params[key])
        self.rt = RTSystem(self.problem)
        self.ssgs = SSGS(self.problem)
        self.population = np.empty(self.params['popSize'], dtype=ActivityList)
        self.schedules = np.empty(self.params['popSize'], dtype=Schedule)
        self.makespans = np.empty(self.params['popSize'], dtype=int)
        self.generated_schedules = 0
        self._generate_new(self.population, self.params['popSize'])
        self._evaluate_population()

    def _generate_new(self, population, size):
        for i in xrange(size):
            population[i] = ActivityList(self.problem).generate_random()

    def _evaluate_population(self):
        for index, al in enumerate(self.population):
            schedule = self.ssgs.get_schedule(al)
            self.generated_schedules += 1
            self.rt.update(schedule)
            schedule.shift(schedule.RIGHT_SHIFT)
            self.generated_schedules += 1
            self.schedules[index] = schedule
            self.makespans[index] = schedule.makespan
        for index, schedule in enumerate(self.schedules):
            self.population[index] = schedule.serialize()
        self.indices = np.argsort(self.makespans)

    def _mutate(self):
        num_mutate = self.params['Rmut'] * self.params['popSize']
        mutants = np.random.choice(self.population, num_mutate, replace=False)
        excluding_activities = self.rt.get_excluding_activities()
        for al in mutants:
            for act in excluding_activities:
                al.shift(act, random.choice((ActivityList.LEFT_SHIFT, ActivityList.RIGHT_SHIFT)), self.params['dist'])
        return mutants

    def _crossover(self, newPopulation):
        num_cross = int(self.params['Rcross'] * self.params['popSize'])
        crossovers = np.empty(num_cross, dtype=ActivityList)
        for i in range(num_cross):
            if random.random() <= 0.3:
                parent1 = random.choice(newPopulation)
            else:
                parent1 = random.choice(self.population)
            parent2 = random.choice(self.population)
            c1 = random.randint(0, self.problem.num_activities - 1)
            c2 = random.randint(c1, self.problem.num_activities - 1)
            crossovers[i] = parent1.crossover(parent2, c1, c2)
        return crossovers

    def step(self):
        newPopulation = np.empty((self.params['popSize']), dtype=ActivityList)
        num_copy = self.params['numRcopy']
        num_new = self.params['numRnew']
        num_mut = self.params['numRmut']
        num_cross = self.params['numRcross']
        # copy best als to new population
        if num_copy > 0:
            newPopulation[:num_copy] = self.population[self.indices][:num_copy]
            offset = num_copy
        # generate new
        if num_new > 0:
            self._generate_new(newPopulation[offset:offset+num_new], num_new)
            offset += num_new
        # mutation
        if num_mut > 0:
            newPopulation[offset:offset+num_mut] = self._mutate()
            offset += num_mut
        # crossover
        if num_cross > 0:
            newPopulation[offset:offset+num_cross] = self._crossover(newPopulation[:offset])
        #replace population with newPopulation
        self.population = newPopulation
        #evaluate
        self._evaluate_population()

    @property
    def best(self):
        return self.schedules[self.indices][0]

    def run(self):
        while self.generated_schedules < self.params['schedule_limit']:
            self.step()






