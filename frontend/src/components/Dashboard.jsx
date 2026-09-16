import PredictionForm from "./PredictionForm";
import EnergyChart from "./EnergyChart";


function Dashboard(){


    return(

        <div className="min-h-screen bg-gray-950 text-white p-8">


            <h1 className="text-4xl font-bold text-cyan-400">
                PowerPredict AI
            </h1>


            <p className="text-gray-400 mt-2">
                AI-based Electricity Demand Forecasting System
            </p>



            <div className="mt-10 grid md:grid-cols-2 gap-8">


                <PredictionForm />

                <EnergyChart />

            </div>


        </div>

    )

}


export default Dashboard;