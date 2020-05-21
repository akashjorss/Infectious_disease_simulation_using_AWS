import React from 'react';
import './App.css';
import {AmplifyAuthenticator, AmplifySignIn, AmplifySignOut} from '@aws-amplify/ui-react'
import Auth from "@aws-amplify/auth";
import SimulationRunner from './SimulationRunner'

function App() {
    Auth.configure({
        userPoolId: "us-east-1_XdMtRyhXb",
        userPoolWebClientId: "27oqm7qb9fetpssarl4dsdvidu",
        region: "us-east-1"
    }),
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