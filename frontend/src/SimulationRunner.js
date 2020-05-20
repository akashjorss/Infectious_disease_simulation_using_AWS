import React, {Component} from 'react';
import simulation_backend from './ApiClient'


const formStyle = {
    "display": "table",
    "text-align": "center",
    "background-color": 'rgba(27, 123, 179, 0.637)',
    "padding": '2em',
    "border-radius": "0.5em",
    "width": "35 %"
}

const inputText = {
    "display": "table-cell",
    "font-family": "Jost",
    "border": "1px solid wheat",
    "text-align": "left",
    "width": "20em",
    "padding": "1em",
    "border-radius": ".5em",
    "text-shadow": "grey",
    "margin": "1em"
}

const labelStyle = {
    "display": "table-cell"
}

export class SimulationRunner extends Component {
    state = {
        population: '',
        distance: '',
    }

    render() {
        return (
            <div>
                <form action="" style={formStyle} onSubmit={this.handleSubmit}>
                    <p>
                        <label htmlFor="points" id="pl" style={labelStyle}>Population</label>
                        <input type="text" style={inputText} placeholder="Enter number of data points" name="points"
                               id="points" onChange={this.handleChange}/>
                    </p>
                    <p>
                        <label htmlFor="distance" id="dl" style={labelStyle}>Infectious threshold</label>
                        <input type="text" style={inputText} placeholder="Enter minimum infecting distance"
                               name="distance"
                               id="distance" onChange={this.handleChange}/>
                    </p>
                    <input type="submit" value="simulate"/>

                </form>
            </div>
        );
    }

    handleChange = event => {
        var x = event.target;
        if (x.id === "points") {
            this.setState({population: x.value})
        }
        if (x.id === "distance") {
            this.setState({distance: x.value})

        }
    }
    handleSubmit = event => {
        event.preventDefault();
        const params = {
            population: this.state.population,
            distance: this.state.distance
        };
        simulation_backend.post("simulate", {params})
            .then(res => {
                document.getElementById("pl").innerHTML = res;
                // document.getElementById("pl").innerHTML = JSON.parse(JSON.stringify(res.data.simulation_id));
                // console.log(res.data);
            })
            .catch(error => {
                console.log(error);
            })
    }


}

export default SimulationRunner;