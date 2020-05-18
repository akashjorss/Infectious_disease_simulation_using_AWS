import React from 'react';
import axios from 'axios'
import './App.css';
import {AmplifyAuthenticator, AmplifySignIn, AmplifySignOut} from '@aws-amplify/ui-react'
import Auth from "@aws-amplify/auth";
import SimulationRunner from './SimulationRunner'

function App() {
    Auth.configure({
        userPoolId: "us-east-1_cNxGqM6Qf",
        userPoolWebClientId: "2mjs8c33p7qvk1mrv8t8ijdbjm",
        region: "us-east-1"
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