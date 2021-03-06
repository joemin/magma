/*
Copyright (c) Facebook, Inc. and its affiliates.
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
*/

// Package main implements WiFi AAA server
package main

import (
	"log"

	"github.com/golang/protobuf/proto"

	"magma/feg/cloud/go/protos/mconfig"
	"magma/feg/gateway/registry"
	"magma/feg/gateway/services/aaa/protos"
	"magma/feg/gateway/services/aaa/servicers"
	"magma/feg/gateway/services/aaa/store"
	"magma/orc8r/cloud/go/service"
	managed_configs "magma/orc8r/gateway/mconfig"
)

const AAAServiceName = "aaa_server"

func main() {
	// Create a shared Session Table
	sessions := store.NewMemorySessionTable()

	// Create the EAP AKA Provider service
	srv, err := service.NewServiceWithOptions(registry.ModuleName, registry.AAA_SERVER)
	if err != nil {
		log.Fatalf("Error creating AAA service: %s", err)
	}
	aaaConfigs := &mconfig.AAAConfig{}
	err = managed_configs.GetServiceConfigs(AAAServiceName, aaaConfigs)
	if err != nil {
		log.Printf("Error getting AAA Server service configs: %s", err)
		aaaConfigs = nil
	}
	acct, _ := servicers.NewAccountingService(sessions, proto.Clone(aaaConfigs).(*mconfig.AAAConfig))
	protos.RegisterAccountingServer(srv.GrpcServer, acct)

	auth, _ := servicers.NewEapAuthenticator(sessions, aaaConfigs, acct)
	protos.RegisterAuthenticatorServer(srv.GrpcServer, auth)

	err = srv.Run()
	if err != nil {
		log.Fatalf("Error running AAA service: %s", err)
	}
}
