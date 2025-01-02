package org.example.theatre.repository;

import org.example.theatre.model.ReservationInfo;
import org.springframework.data.cassandra.repository.CassandraRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface ReservationInfoRepository extends CassandraRepository<ReservationInfo, UUID> {}