from __future__ import print_function, absolute_import, division #makes KratosMultiphysics backward compatible with python 2.6 and 2.7

# Import system python modules
import time as timer
import sys
import os

# Import kratos core and applications
import KratosMultiphysics
import KratosMultiphysics.SolidMechanicsApplication     as KratosSolid
import KratosMultiphysics.ExternalSolversApplication    as KratosSolvers

sys.stdout.flush()

class Solution(object):

    def __init__(self):
        
        # Time control starts        
        print(timer.ctime())

        sys.stdout.flush()
        
        # Measure process time
        self.t0p = timer.clock()
        
        # Measure wall time
        self.t0w = timer.time()
                
        # Import input
        parameter_file = open("ProjectParameters.json",'r')
        self.ProjectParameters = KratosMultiphysics.Parameters(parameter_file.read())

        # Set echo level
        self.echo_level = self.ProjectParameters["problem_data"]["echo_level"].GetInt()

        # Defining the number of threads
        num_threads =  self._get_parallel_size()

        print(" ")
        print("::[KSM Simulation]:: [OMP USING",num_threads,"THREADS ]")

        # Output settings start
        self.problem_path = os.getcwd()
        self.problem_name = self.ProjectParameters["problem_data"]["problem_name"].GetString()     

   
    def Run(self):

        self.Initialize()
        
        self.Solve()

        self.Finalize()
        
        
    def Initialize(self):

        # Start model
        self.model  = self._get_model()

        # Start solver
        computing_model_part = self.model.GetComputingModelPart()
        self.solver = self._get_solver(computing_model_part)

        self.solver.SetEchoLevel(self.echo_level)
        solver_variables = self.solver.GetVariables()
        self.model.SetVariables(solver_variables)

        # Start processes
        #self.processes = self._get_processes()
        
        #processes_variables = self.processes.GetVariables()
        #self.model.SetVariables(processes_variables)
        
        self.process_info = self.model.GetProcessInfo()
        
        # Read model
        self.model.ImportModel()

        # Start processes
        self.processes = self._get_processes()
        
        sys.stdout.flush()

        # Initialize solver buffer
        if( self._is_not_restarted() ):
            self.solver.SetBuffer()       
            
        # Import materials
        self.main_model_part = self.model.GetMainModelPart() 
        self._import_materials()
        
        self.processes.ExecuteInitialize()

        # Print model_part and properties
        if(self.echo_level>0):
            print("")
            print(self.main_model_part)
            for properties in self.main_model_part.Properties:
                print(properties)

               
        # Start graphical output (GiD)
        output_model_part = self.model.GetOutputModelPart()
        self.output = self._get_graphical_output(output_model_part)
        self.output.ExecuteInitialize()

        print(" ")
        print("::[KSM Simulation]:: Analysis -START- ")

        # First execution before solution loop
        self.processes.ExecuteBeforeSolutionLoop()

        # Writing a initial state results file or single file (if no restart)
        if( self._is_not_restarted() ):
            self.output.ExecuteBeforeSolutionLoop()
                
        # Sets strategies, builders, linear solvers, schemes and solving info, and fills the buffer
        self.processes.ExecuteInitializeSolutionStep() #trick to use elimintation builder
        self.solver.Initialize()
       
        # Set time settings
        self.step       = self.process_info[KratosMultiphysics.STEP]
        self.time       = self.process_info[KratosMultiphysics.TIME]

        self.delta_time = self.process_info[KratosMultiphysics.DELTA_TIME]
        self.end_time   = self.solver.GetEndTime()

        sys.stdout.flush()

        
    def Solve(self):
        
        # Solving the problem (time integration)
        while(self.time < self.end_time):
            
            self.InitializeSolutionStep()
            self.SolveSolutionStep()
            self.FinalizeSolutionStep()

            sys.stdout.flush()
                  
    def InitializeSolutionStep(self):
        
        # Current time parameters
        self.delta_time = self.process_info[KratosMultiphysics.DELTA_TIME]

        self.time = self.time + self.delta_time
        self.step = self.step + 1

        self.process_info[KratosMultiphysics.STEP] = self.step
        
        self.main_model_part.CloneTimeStep(self.time) 

        print(" [STEP:",self.step," TIME:","{0:1.{1}f}".format(self.time,6),"]")

        # Processes to be executed at the begining of the solution step
        self.processes.ExecuteInitializeSolutionStep()

        self.output.ExecuteInitializeSolutionStep()

        self.solver.InitializeSolutionStep()
        
        
    def SolveSolutionStep(self):

        self.clock_time = self._start_time_measuring();

        #self.solver.Predict()

        #self.solver.SolveSolutionStep()

        #self.solver.FinalizeSolutionStep()

        self.solver.Solve()

        self._stop_time_measuring(self.clock_time,"Solving", False);

        
    def FinalizeSolutionStep(self):
        
        self.output.ExecuteFinalizeSolutionStep()

        # Processes to be executed at the end of the solution step
        self.processes.ExecuteFinalizeSolutionStep()

        # Processes to be executed before witting the output      
        self.processes.ExecuteBeforeOutputStep()

        # Write output results GiD: (frequency writing is controlled internally)
        if(self.output.IsOutputStep()):
            self.output.PrintOutput()

        # Processes to be executed after witting the output
        self.processes.ExecuteAfterOutputStep()
        

    def Finalize(self):
        
        # Ending the problem (time integration finished)
        self.output.ExecuteFinalize()

        self.processes.ExecuteFinalize()

        print("::[KSM Simulation]:: Analysis -END- ")
        print(" ")

        # Check solving information for any problem
        # self.solver.InfoCheck() # InfoCheck not implemented yet.

        # Measure process time
        tfp = timer.clock()

        # Measure wall time
        tfw = timer.time()

        print("::[KSM Simulation]:: [Elapsed Time = %.2f" % (tfw - self.t0w),"seconds] (%.2f" % (tfp - self.t0p),"seconds of cpu/s time)")
        print(timer.ctime())

        
    #### Main internal methods ####

    def _is_not_restarted(self):
        if( self.process_info.Has(KratosMultiphysics.IS_RESTARTED) ):
            if( self.process_info[KratosMultiphysics.IS_RESTARTED] == False ):
                return True
            else:
                return False
        else:
            return True
        
    def _get_model(self):            
        import model_manager
        return (model_manager.ModelManager(self.ProjectParameters["model_settings"]))
        
    def _get_solver(self, computing_model_part):
        solver_module = __import__(self.ProjectParameters["solver_settings"]["solver_type"].GetString())
        return (solver_module.CreateSolver(computing_model_part, self.ProjectParameters["solver_settings"]["Parameters"]))
      
    def _import_materials(self):
        # Assign material to model_parts (if Materials.json exists)
        import process_factory

        if os.path.isfile("Materials.json"):
            materials_file = open("Materials.json",'r')
            MaterialParameters = KratosMultiphysics.Parameters(materials_file.read())
    
            if(MaterialParameters.Has("material_models_list")):

                import KratosMultiphysics.ConstitutiveModelsApplication as KratosMaterials
                
                domain_model = self.model.GetModel()
        
                assign_materials_processes = process_factory.KratosProcessFactory(domain_model).ConstructListOfProcesses( MaterialParameters["material_models_list"] )

                for process in assign_materials_processes:
                    process.Execute()
                                
        elif os.path.isfile("materials.py"): # legacy
            
            import constitutive_law_python_utility as constitutive_law_utils

            constitutive_law = constitutive_law_utils.ConstitutiveLawUtility(self.main_model_part, self.process_info[KratosMultiphysics.SPACE_DIMENSION]);

            constitutive_law.Initialize();
        
            problem_path = os.getcwd()

            print("   Reading constitutive law from file :" + os.path.join(problem_path, "materials") + ".py ")

        else:
            print(" No Materials.json or Materials.py found ")
            
           
    def _get_processes(self):
        # Obtain the list of the processes to be applied
        import process_handler

        process_parameters = KratosMultiphysics.Parameters("{}") 
        process_parameters.AddValue("echo_level", self.ProjectParameters["problem_data"]["echo_level"])
        process_parameters.AddValue("constraints_process_list", self.ProjectParameters["constraints_process_list"])
        process_parameters.AddValue("loads_process_list", self.ProjectParameters["loads_process_list"])
        if( self.ProjectParameters.Has("problem_process_list") ):
            process_parameters.AddValue("problem_process_list", self.ProjectParameters["problem_process_list"])
        if( self.ProjectParameters.Has("output_process_list") ):
            process_parameters.AddValue("output_process_list", self.ProjectParameters["output_process_list"])

        domain_model = self.model.GetModel()
        return (process_handler.ProcessHandler(domain_model, process_parameters))
        
    def _get_graphical_output(self, output_model_part):
        import gid_output_process
        self.output_settings = self.ProjectParameters["output_configuration"]
        return (gid_output_process.GiDOutputProcess(output_model_part,self.problem_name,self.output_settings))
                     
    def _set_parallel_size(self, num_threads):
        parallel = KratosMultiphysics.OpenMPUtils()
        parallel.SetNumThreads(int(num_threads))

    def _get_parallel_size(self):
        parallel = KratosMultiphysics.OpenMPUtils()
        return parallel.GetNumThreads()    
    
    def _start_time_measuring(self):
        # Measure process time
        time_ip = timer.clock()
        return time_ip

    def _stop_time_measuring(self, time_ip, process, report):
        # Measure process time
        time_fp = timer.clock()
        if( report ):
            used_time = time_fp - time_ip
            print("::[KSM Simulation]:: [ %.2f" % round(used_time,2),"s", process," ] ")


if __name__ == "__main__": 
    Solution().Run()
    
