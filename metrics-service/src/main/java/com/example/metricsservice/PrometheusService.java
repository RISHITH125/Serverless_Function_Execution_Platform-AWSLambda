package com.example.metricsservice;

import com.google.common.util.concurrent.AtomicDouble;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class PrometheusService {

    private final Map<String, Metrics> containerMetricsMap = new ConcurrentHashMap<>();

    private final MeterRegistry meterRegistry;

    @Autowired
    public PrometheusService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    public void updateChanges() {
        containerMetricsMap.forEach((route, metrics) -> {
            Gauge.builder(route, metrics.executionTime, AtomicDouble::get)
                    .register(meterRegistry);
        });
    }

    public void update(String route , double executionTime) {
        if (!containerMetricsMap.containsKey(route)) {
            containerMetricsMap.put(route, new Metrics());
        }
        containerMetricsMap.get(route).executionTime.set(executionTime);
    }

    static class Metrics {
        AtomicDouble executionTime = new AtomicDouble(0);
    }
}
