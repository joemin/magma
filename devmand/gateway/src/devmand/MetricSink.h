// Copyright (c) 2016-present, Facebook, Inc.
// All rights reserved.
//
// This source code is licensed under the BSD-style license found in the
// LICENSE file in the root directory of this source tree. An additional grant
// of patent rights can be found in the PATENTS file in the same directory.

#pragma once

#include <string>

namespace devmand {

/* An abstraction of a class which handles metrics.
 */
class MetricSink {
 public:
  MetricSink() = default;
  virtual ~MetricSink() = default;
  MetricSink(const MetricSink&) = delete;
  MetricSink& operator=(const MetricSink&) = delete;
  MetricSink(MetricSink&&) = delete;
  MetricSink& operator=(MetricSink&&) = delete;

 public:
  virtual void setGauge(
      const std::string& key,
      double value,
      const std::string& label_name,
      const std::string& label_value) = 0;
  virtual void setGauge(const std::string& key, double value) = 0;
};

} // namespace devmand
