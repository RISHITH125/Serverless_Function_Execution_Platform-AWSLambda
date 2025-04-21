package com.example.metricsservice;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MetricsController {

    PrometheusService prometheusService;

    @Autowired
    public MetricsController(PrometheusService prometheusService) {
        this.prometheusService = prometheusService;
    }

    @PostMapping("/update/metrics")
    public ResponseEntity<Void> registerRouteExecutionTime(@RequestBody Request request) {
        String route = request.route;
        Double executionTime = request.executiontime;

        prometheusService.update(route, executionTime);
        prometheusService.updateChanges();
        return ResponseEntity.noContent().build();
    }

    static class Request {

        public String route;
        public Double executiontime;

    }

}
