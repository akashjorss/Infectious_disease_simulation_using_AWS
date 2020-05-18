import React from 'react';
import axios from 'axios'
import './App.css';
import {AmplifyAuthenticator, AmplifySignIn, AmplifySignOut} from '@aws-amplify/ui-react'
import Auth from "@aws-amplify/auth";
import SimulationRunner from './SimulationRunner'

function App() {
    Auth.configure({
        userPoolId: "us-east-2_g8pVQyn5v",
        userPoolWebClientId: "4fstkb0vq4uitagigv85jl02ms",
        region: "us-east-2"
    })
    return (
        <div className="App">
            <header className="App-header">
                <AmplifyAuthenticator>
                    <AmplifySignIn headerText="Sign into Infection Simulation" slot="sign-in">
                        <div slot="secondary-footer-content"></div>
                    </AmplifySignIn>

                    <div>
                        Simulation App
                        <SimulationRunner/>
                        <AmplifySignOut/>
                    </div>
                </AmplifyAuthenticator>
            </header>
        </div>
    );
}

export default App