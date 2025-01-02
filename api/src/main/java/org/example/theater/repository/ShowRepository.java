package com.example.theater.repository;

import com.example.theater.model.Show;
import org.springframework.data.cassandra.repository.CassandraRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface ShowRepository extends CassandraRepository<Show, UUID> {}