<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow">
        <div class="container-fluid">
            <router-link to="/energy" class="navbar-brand fw-bold">SHEMS</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
            aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <!-- <li class="nav-item">
                    <router-link to="/" class="nav-link">Home</router-link>
                    </li> -->
                    <li class="nav-item">
                    <router-link to="/energy" class="nav-link">Dashboard</router-link>
                    </li>
                    <!-- <li class="nav-item">
                    <router-link to="/energy-data" class="btn btn-primary">Energy Data</router-link>
                    </li> -->
                    <li class="nav-item">
                    <router-link to="/community" class="nav-link">Community</router-link>
                    </li>
                    <li class="nav-item">
                    <router-link to="/automation" class="nav-link">Automation</router-link>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="btn btn-danger" href="/login/">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>