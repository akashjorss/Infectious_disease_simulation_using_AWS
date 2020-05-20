import axios from 'axios'
import Auth from "@aws-amplify/auth";

const simulation_backend = axios.create({
    baseURL: "https://q028j3qc20.execute-api.us-east-1.amazonaws.com/test"
});

simulation_backend.interceptors.request.use(function (config) {
    return Auth.currentSession()
        .then(session => {
            // User is logged in. Set auth header on all requests
            config.headers.Authorization = 'Bearer ' + session.idToken.jwtToken
            return Promise.resolve(config)
        })
        .catch(() => {
            // No logged-in user: don't set auth header
            return Promise.resolve(config)
        })
});

export default simulation_backend;