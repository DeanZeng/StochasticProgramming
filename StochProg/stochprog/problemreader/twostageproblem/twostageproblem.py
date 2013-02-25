import copy

from stochprog.problemreader.twostageproblem.variable import Variable,\
    VariableType
from stochprog.problemreader.twostageproblem.constraint import Constraint
from stochprog.problemreader.twostageproblem.realization import Realization
from stochprog.problemreader.twostageproblem.scenario import Scenario

class TwoStageProblem(object):
    
    def __init__(self):
        self._root_scenario = Scenario(0)
        self._scenarios = []
        self._realizations = []
    
        
    def get_root_scenario(self):
        return self._root_scenario


    def get_scenarios(self):
        return self._scenarios 
    
        
    def add_root_variable(self, name, cost, stage, var_type=VariableType.REAL):
        var_id = len(self._root_scenario.get_variables())
        var = Variable(var_id, name, cost, var_type, stage)
        
        self._root_scenario.set_var_coef(var)
        
        return var_id
    
    
    def add_root_constraint(self, name, constr_type, vars_and_coefficients, rhs, stage):
        constr_id = len(self._root_scenario.get_constraints())
        constr = Constraint(constr_id, name, constr_type, stage)
        constr.set_rhs(rhs)
        for var_id, coef in vars_and_coefficients:
            constr.set_var_coef(var_id, coef)
            
        self._root_scenario.add_constraint(constr)
        
        return constr_id
    
    
    def add_realization(self, probability, cost_changes, coefficient_changes, rhs_changes):
        self._realizations.append(Realization(probability, cost_changes, coefficient_changes, rhs_changes))
    
    
    def _apply_realization_to_scenario(self, scen, realization):
        prob = realization.get_probability()
        cost_changes = realization.get_cost_changes()
        coefficient_changes = realization.get_coefficient_changes()
        rhs_changes = realization.get_rhs_changes()
        
        for var_id, cost in cost_changes:
            scen.set_var_cost(var_id, cost)
        scen.set_probability(prob)
        scen.update_second_stage_costs()
        
        for var_id, constr_id, coef in coefficient_changes:
            scen.set_var_coef_in_constr(var_id, constr_id, coef)
        
        for constr_id, rhs in rhs_changes:
            scen.set_constr_rhs(constr_id, rhs)
    
    
    def generate_scenarios(self):
        n = len(self._realizations)
        root_vars = self._root_scenario.get_variables()
        root_constr = self._root_scenario.get_constraints()
        
        for i in xrange(n):
            scen = Scenario(i + 1)
            for var in root_vars:
                scen.set_var_coef(copy.deepcopy(var))
            for constr in root_constr:
                scen.add_constraint(copy.deepcopy(constr))
            self._apply_realization_to_scenario(scen, self._realizations[i - 1])
            self._scenarios.append(scen)
            
        return self._scenarios
            
