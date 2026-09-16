import { useState } from "react";
import axios from "axios";


function PredictionForm(){

    const [formData, setFormData] = useState({

        "generation solar": "",
        "generation wind onshore": "",
        "forecast solar day ahead": "",
        "forecast wind onshore day ahead": "",
        temp: "",
        humidity: "",
        pressure: "",
        wind_speed: "",
        hour: "",
        day: "",
        month: "",
        weekday: "",
        is_weekend: ""

    });


    const [prediction, setPrediction] = useState(null);



    const handleChange = (e) => {

        setFormData({

            ...formData,
            [e.target.name]: e.target.value

        });

    };



    const handlePredict = async () => {

        try {


            const response = await axios.post(

                "http://127.0.0.1:5000/predict",

                {

                    "generation solar": Number(formData["generation solar"]),

                    "generation wind onshore": Number(formData["generation wind onshore"]),

                    "forecast solar day ahead": Number(formData["forecast solar day ahead"]),

                    "forecast wind onshore day ahead": Number(formData["forecast wind onshore day ahead"]),

                    temp: Number(formData.temp),

                    humidity: Number(formData.humidity),

                    pressure: Number(formData.pressure),

                    wind_speed: Number(formData.wind_speed),

                    hour: Number(formData.hour),

                    day: Number(formData.day),

                    month: Number(formData.month),

                    weekday: Number(formData.weekday),

                    is_weekend: Number(formData.is_weekend)

                }

            );


            setPrediction(

                Number(response.data["Predicted Power Load"])

            );


        }


        catch(error){

            console.log(error);

        }

    };



    return (

        <div className="bg-gray-900 p-6 rounded-xl shadow-lg">


            <h2 className="text-2xl font-semibold text-cyan-300">

                Energy Prediction

            </h2>



            <div className="grid grid-cols-2 gap-3 mt-5">


                {

                    Object.keys(formData).map((key)=>(


                        <input


                            key={key}


                            name={key}


                            value={formData[key]}


                            onChange={handleChange}


                            placeholder={key}


                            className="p-3 rounded bg-gray-800 text-white"


                        />


                    ))

                }


            </div>




            <button


                onClick={handlePredict}


                className="mt-5 bg-cyan-500 px-5 py-3 rounded-lg text-black font-bold"


            >

                Predict Demand


            </button>




            {

                prediction &&


                <h3 className="mt-5 text-xl text-green-400">


                    Predicted Power Load:{" "}

                    {prediction.toFixed(2)}


                </h3>


            }


        </div>

    );

}



export default PredictionForm;